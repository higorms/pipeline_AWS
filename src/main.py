import os
import json
from datetime import date, timedelta, datetime
from dotenv import load_dotenv

from config.logging_config import setup_logging, get_logger
from application.use_cases.extract_b3_data import ExtractB3DataUseCase
from application.use_cases.upload_parquet_to_s3 import UploadParquetToS3UseCase
from infrastructure.data_sources.yfinance_data_source import YFinanceDataSource
from infrastructure.storage.s3_storage_repository import S3StorageRepository
from config.symbols_loader import load_symbols

# Configuração do logging
setup_logging(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = get_logger(__name__)


def run_pipeline(event=None):
    """
    Função principal da aplicação.
    Executa o pipeline de extração e ingestão de dados da B3.

    Args:
        event: Evento Lambda com configurações opcionais (bucket_name, symbols, days_back)

    Returns:
        dict: Resultado da execução com status e estatísticas
    """
    # Carrega variáveis de ambiente
    load_dotenv()

    # Configurações (aceita override do evento Lambda)
    if event is None:
        event = {}

    bucket_name = event.get('bucket_name') or os.getenv('AWS_S3_BUCKET_NAME', 'meu-bucket-exemplo')
    region = event.get('region') or os.getenv('AWS_REGION', 'us-east-1')

    # Símbolos a serem extraídos (ações da B3)
    default_symbols = load_symbols()
    symbols = event.get('symbols', default_symbols)

    # Período de extração (dia anterior ou configurado)
    days_back = event.get('days_back', 1)
    end_date = date.today()
    start_date = date.today() - timedelta(days=days_back)

    logger.info("="*70)
    logger.info("PIPELINE DE EXTRAÇÃO DE DADOS DA B3")
    logger.info("="*70)
    logger.info(f"Bucket: {bucket_name} | Região: {region}")
    logger.info(f"Símbolos: {len(symbols)} | Período: {start_date} a {end_date}")

    # Configuração das dependências (Dependency Injection)
    data_source = YFinanceDataSource()
    storage_repository = S3StorageRepository(region_name=region)

    extract_use_case = ExtractB3DataUseCase(data_source)
    upload_use_case = UploadParquetToS3UseCase(storage_repository)

    try:
        # Etapa 1: Extração de dados da B3
        logger.info("Iniciando extração de dados...")
        df = extract_use_case.execute(symbols, start_date, end_date)

        # Etapa 2: Particionamento e upload por data
        logger.info("Iniciando particionamento e upload...")
        unique_dates = sorted(df['date'].unique())
        logger.info(f"Particionando em {len(unique_dates)} datas")

        success_count = 0
        fail_count = 0

        for data_partition in unique_dates:
            df_partition = df[df['date'] == data_partition]

            # Parsear a data para extrair year, month, day
            partition_date = datetime.strptime(str(data_partition), '%Y-%m-%d')
            year = partition_date.year
            month = partition_date.month
            day = partition_date.day

            # Gerar timestamp (Unix timestamp em segundos)
            timestamp = int(datetime.now().timestamp())

            # Formato: raw/year=2025/month=10/day=05/stocks_{timestamp}.parquet
            s3_key = (
                f"raw/year={year}/month={month:02d}/day={day:02d}/"
                f"stocks_{timestamp}.parquet"
            )

            logger.debug(f"Partição {data_partition}: {len(df_partition)} registros -> s3://{bucket_name}/{s3_key}")

            success = upload_use_case.execute(
                dataframe=df_partition,
                bucket_name=bucket_name,
                s3_key=s3_key
            )

            if success:
                success_count += 1
                logger.info(f"✓ Partição {data_partition} enviada com sucesso")
            else:
                fail_count += 1
                logger.error(f"✗ Falha ao enviar partição {data_partition}")

        # Resumo final
        logger.info("="*70)
        logger.info(f"Pipeline concluído: {len(df)} registros | {len(unique_dates)} partições | {success_count} uploads")
        if fail_count > 0:
            logger.warning(f"{fail_count} uploads falharam")
        logger.info("="*70)

        # Retorna resultado estruturado
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Pipeline executado com sucesso',
                'total_records': len(df),
                'partitions': len(unique_dates),
                'successful_uploads': success_count,
                'failed_uploads': fail_count
            })
        }

    except Exception as e:
        logger.error(f"Erro no pipeline: {e}", exc_info=True)

        # Retorna erro estruturado
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Erro no pipeline',
                'error': str(e)
            })
        }


def lambda_handler(event, context):
    """
    Handler para AWS Lambda.

    Args:
        event: Evento Lambda com parâmetros opcionais
        context: Contexto de execução Lambda

    Returns:
        dict: Resposta com statusCode e body
    """
    logger.info(f"Lambda invoked: {json.dumps(event)}")
    return run_pipeline(event)


def main():
    """
    Função para execução standalone (fora do Lambda).
    """
    result = run_pipeline()
    logger.info(f"Resultado: {result}")


if __name__ == "__main__":
    main()
