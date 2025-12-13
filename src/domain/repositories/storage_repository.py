"""
Interface do repositório de armazenamento (Storage Repository).
Define o contrato que deve ser implementado pela camada de infraestrutura.
"""
from abc import ABC, abstractmethod
from typing import Any


class StorageRepository(ABC):
    """
    Interface para operações de armazenamento.
    """

    @abstractmethod
    def upload_data(
        self,
        data: Any,
        bucket_name: str,
        s3_key: str,
        format: str = 'parquet'
    ) -> bool:
        """
        Faz upload de dados direto da memória.

        Args:
            data: Dados a serem enviados (DataFrame pandas)
            bucket_name: Nome do bucket de destino
            s3_key: Chave/caminho do arquivo no S3
            format: Formato do arquivo (parquet, csv, etc)

        Returns:
            True se sucesso, False caso contrário
        """
        pass
