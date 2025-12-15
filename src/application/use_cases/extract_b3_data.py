"""
Use Case: Extração de dados da B3.
"""
from datetime import date
from typing import List
import pandas as pd

from domain.repositories.data_source_repository import DataSourceRepository


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
        
        print(f"\n📥 Iniciando extração de {len(symbols)} símbolos...")
        print(f"   Período: {start_date} até {end_date}")
        
        df = self.data_source.extract_daily_data(symbols, start_date, end_date)
        
        print(f"\n✓ Extraídos {len(df)} registros no total")
        print(f"   Datas únicas: {df['date'].nunique()}")
        print(f"   Símbolos únicos: {df['symbol'].nunique()}")
        
        return df
