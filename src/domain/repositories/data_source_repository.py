"""
Interface do repositório de fonte de dados.
Define o contrato para extração de dados da B3.
"""
from abc import ABC, abstractmethod
from datetime import date
import pandas as pd
from typing import List


class DataSourceRepository(ABC):
    """
    Interface para extração de dados de ações/índices.
    """

    @abstractmethod
    def extract_daily_data(
        self,
        symbols: List[str],
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Extrai dados diários de ações/índices.

        Args:
            symbols: Lista de códigos das ações (ex: ['PETR4.SA', 'VALE3.SA'])
            start_date: Data inicial
            end_date: Data final

        Returns:
            DataFrame com colunas: date, symbol, open, high, low, close, volume
        """
        pass
