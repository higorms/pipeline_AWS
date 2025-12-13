"""
Ponto de entrada da aplicação.
Configura as dependências e executa o caso de uso.
"""
import os
from dotenv import load_dotenv

from application.use_cases.upload_parquet_to_s3 import UploadParquetToS3UseCase
from infrastructure.storage.s3_storage_repository import S3StorageRepository


def main():
    """
    Função principal da aplicação.
    """
    # Carrega variáveis de ambiente
    load_dotenv()

    # Configurações
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'meu-bucket-exemplo')
    region = os.getenv('AWS_REGION', 'us-east-1')

    # Configuração das dependências (Dependency Injection)
    storage_repository = S3StorageRepository(region_name=region)
    upload_use_case = UploadParquetToS3UseCase(storage_repository)

    # TODO: Função de extração de dados e criação do dataframe

    # TODO: Função de envio tem que particionar os dados por dia

    try:
        success = upload_use_case.execute(
            dataframe=df,
            bucket_name=bucket_name,
            s3_key="processed/exemplo_funcionarios.parquet"
        )

        if success:
            print("\n✓ DataFrame enviado com sucesso para S3!")
    except Exception as e:
        print(f"\n❌ Erro ao enviar DataFrame: {e}")

    print("\n" + "=" * 70)
    print("  EXECUÇÃO FINALIZADA")
    print("=" * 70)


if __name__ == "__main__":
    main()
