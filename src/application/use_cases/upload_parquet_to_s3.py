"""
Use Case: Upload de DataFrame como Parquet para S3.
Contém a lógica de negócio da aplicação.
"""
import pandas as pd

from ...domain.repositories.storage_repository import StorageRepository


class UploadParquetToS3UseCase:
    """
    Caso de uso para upload de DataFrames como Parquet para S3.
    """

    def __init__(self, storage_repository: StorageRepository):
        """
        Inicializa o caso de uso com suas dependências.

        Args:
            storage_repository: Implementação do repositório de armazenamento
        """
        self.storage_repository = storage_repository

    def execute(
        self,
        dataframe: pd.DataFrame,
        bucket_name: str,
        s3_key: str
    ) -> bool:
        """
        Executa o upload de um DataFrame diretamente para S3 como Parquet.

        Args:
            dataframe: DataFrame pandas
            bucket_name: Nome do bucket S3
            s3_key: Chave/caminho do arquivo no S3

        Returns:
            True se sucesso, False caso contrário

        Raises:
            ValueError: Se o DataFrame estiver vazio
        """
        # Validações de negócio
        if dataframe.empty:
            raise ValueError("DataFrame não pode estar vazio")

        if not s3_key.endswith('.parquet'):
            s3_key = f"{s3_key}.parquet"

        # Delega a operação para o repositório
        return self.storage_repository.upload_data(
            data=dataframe,
            bucket_name=bucket_name,
            s3_key=s3_key,
            format='parquet'
        )
