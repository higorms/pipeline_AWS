"""
Use Case: Extração de dados da B3.
"""
import logging
from datetime import date
from typing import List
import pandas as pd

from domain.repositories.data_source_repository import DataSourceRepository

logger = logging.getLogger(__name__)


class ExtractB3DataUseCase:
    """
    Caso de uso para extração de dados da B3.
    """

    def __init__(self, data_source: DataSourceRepository):
        """
        Inicializa o caso de uso com a fonte de dados.

        Args:
            data_source: Implementação da interface DataSourceRepository
        """
        self.data_source = data_source

    def execute(
        self,
        symbols: List[str],
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Extrai dados da B3 para os símbolos e período especificados.

        Args:
            symbols: Lista de códigos das ações (ex: ['PETR4.SA', 'VALE3.SA'])
            start_date: Data inicial
            end_date: Data final

        Returns:
            DataFrame com dados extraídos contendo:
            - date: Data do pregão
            - symbol: Código do ativo
            - open: Preço de abertura
            - high: Preço máximo
            - low: Preço mínimo
            - close: Preço de fechamento
            - volume: Volume negociado

        Raises:
            ValueError: Se a lista de símbolos estiver vazia ou datas inválidas
        """
        if not symbols:
            raise ValueError("Lista de símbolos não pode estar vazia")

        if start_date > end_date:
            raise ValueError("Data inicial não pode ser maior que data final")

        logger.info(f"Extraindo {len(symbols)} símbolos ({start_date} a {end_date})")

        df = self.data_source.extract_daily_data(symbols, start_date, end_date)

        logger.info(f"Extração concluída: {len(df)} registros | {df['date'].nunique()} datas | {df['symbol'].nunique()} símbolos")

        return df
