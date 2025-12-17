"""
Implementação concreta do repositório de armazenamento usando AWS S3.
Camada de infraestrutura.
"""
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import io
from typing import Any

from domain.repositories.storage_repository import StorageRepository


class S3StorageRepository(StorageRepository):
    """
    Implementação do repositório de armazenamento usando AWS S3.
    """

    def __init__(self, region_name: str = 'us-east-1'):
        """
        Inicializa o repositório S3.

        Args:
            region_name: Região da AWS
        """
        self.region_name = region_name
        self.s3_client = self._create_s3_client()

    def _create_s3_client(self):
        """
        Cria cliente S3 configurado.

        Returns:
            Cliente boto3 S3

        Raises:
            NoCredentialsError: Se credenciais não forem encontradas
        """
        try:
            client = boto3.client('s3', region_name=self.region_name)
            return client
        except NoCredentialsError as e:
            raise NoCredentialsError(
                "Credenciais AWS não encontradas. "
                "Configure usando AWS CLI ou variáveis de ambiente."
            ) from e

    def upload_data(
        self,
        data: Any,
        bucket_name: str,
        s3_key: str,
        format: str = 'parquet'
    ) -> bool:
        """
        Faz upload de dados direto da memória para S3.

        Args:
            data: Dados a serem enviados (DataFrame pandas)
            bucket_name: Nome do bucket S3
            s3_key: Chave/caminho do arquivo no S3
            format: Formato do arquivo ('parquet' ou 'csv')

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            print(f"📤 Enviando dados para: s3://{bucket_name}/{s3_key}")

            # Converte DataFrame para bytes
            buffer = io.BytesIO()

            if format == 'parquet':
                data.to_parquet(buffer, index=False, engine='fastparquet')
            elif format == 'csv':
                data.to_csv(buffer, index=False)
            else:
                raise ValueError(f"Formato não suportado: {format}")

            # Volta para o início do buffer
            buffer.seek(0)

            # Faz upload
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=buffer.getvalue(),
                ServerSideEncryption='AES256'
            )

            print("✓ Dados enviados com sucesso!")
            return True

        except ClientError as e:
            print(f"❌ Erro AWS: {e.response['Error']['Code']}")
            print(f"   Mensagem: {e.response['Error']['Message']}")
            return False

        except Exception as e:
            print(f"❌ Erro inesperado: {str(e)}")
            return False
