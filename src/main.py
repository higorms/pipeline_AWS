"""
Ponto de entrada da aplicação.
Configura as dependências e executa o caso de uso.
"""
import os
from datetime import date, timedelta, datetime
from dotenv import load_dotenv

from application.use_cases.extract_b3_data import ExtractB3DataUseCase
from application.use_cases.upload_parquet_to_s3 import UploadParquetToS3UseCase
from infrastructure.data_sources.yfinance_data_source import YFinanceDataSource
from infrastructure.storage.s3_storage_repository import S3StorageRepository


def main():
    """
    Função principal da aplicação.
    Executa o pipeline de extração e ingestão de dados da B3.
    """
    # Carrega variáveis de ambiente
    load_dotenv()

    # Configurações
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'meu-bucket-exemplo')
    region = os.getenv('AWS_REGION', 'us-east-1')

    # Símbolos a serem extraídos (ações da B3)
    symbols = [
        '^BVSP',      # Índice Bovespa
        'PETR4.SA',   # Petrobras PN
        'VALE3.SA',   # Vale ON
        'ITUB4.SA',   # Itaú Unibanco PN
        'BBDC4.SA',   # Bradesco PN
        'ABEV3.SA',   # Ambev ON
        'WEGE3.SA',   # WEG ON
        'B3SA3.SA',   # B3 ON
    ]

    # Período de extração (dia anterior)
    end_date = date.today()
    start_date = date.today() - timedelta(days=1)

    print("=" * 70)
    print("  PIPELINE DE EXTRAÇÃO DE DADOS DA B3")
    print("=" * 70)
    print("\n📋 Configurações:")
    print(f"   Bucket S3: {bucket_name}")
    print(f"   Região: {region}")
    print(f"   Símbolos: {len(symbols)}")
    print(f"   Período: {start_date} até {end_date}")

    # Configuração das dependências (Dependency Injection)
    data_source = YFinanceDataSource()
    storage_repository = S3StorageRepository(region_name=region)

    extract_use_case = ExtractB3DataUseCase(data_source)
    upload_use_case = UploadParquetToS3UseCase(storage_repository)

    try:
        # Etapa 1: Extração de dados da B3
        print("\n" + "=" * 70)
        print("  ETAPA 1: EXTRAÇÃO DE DADOS")
        print("=" * 70)

        df = extract_use_case.execute(symbols, start_date, end_date)

        # Etapa 2: Particionamento e upload por data
        print("\n" + "=" * 70)
        print("  ETAPA 2: PARTICIONAMENTO E UPLOAD")
        print("=" * 70)

        unique_dates = sorted(df['date'].unique())
        print(f"\n📦 Particionando dados em {len(unique_dates)} datas...")

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

            # Formato: raw/year=2025/month=10/day=5/stocks_{timestamp}.parquet
            s3_key = (
                f"raw/year={year}/month={month}/day={day}/"
                f"stocks_{timestamp}.parquet"
            )

            print(f"\n📤 Enviando partição {data_partition}...")
            print(f"   Registros: {len(df_partition)}")
            print(f"   Destino: s3://{bucket_name}/{s3_key}")

            success = upload_use_case.execute(
                dataframe=df_partition,
                bucket_name=bucket_name,
                s3_key=s3_key
            )

            if success:
                success_count += 1
                print("   ✓ Sucesso!")
            else:
                fail_count += 1
                print(f"   ❌ Falha ao enviar partição {data_partition}")

        # Resumo final
        print("\n" + "=" * 70)
        print("  RESUMO DA EXECUÇÃO")
        print("=" * 70)
        print(f"\n✓ Total de registros extraídos: {len(df)}")
        print(f"✓ Partições criadas: {len(unique_dates)}")
        print(f"✓ Uploads bem-sucedidos: {success_count}")
        if fail_count > 0:
            print(f"❌ Uploads com falha: {fail_count}")
        print("\n✓ Pipeline executado com sucesso!")

    except Exception as e:
        print(f"\n❌ Erro no pipeline: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("  EXECUÇÃO FINALIZADA")
    print("=" * 70)


if __name__ == "__main__":
    main()
