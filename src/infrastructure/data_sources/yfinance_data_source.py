"""
Implementação da extração de dados usando yfinance.
"""
import yfinance as yf
import pandas as pd
from datetime import date
from typing import List

from domain.repositories.data_source_repository import DataSourceRepository


class YFinanceDataSource(DataSourceRepository):
    """
    Extrai dados da B3 usando a biblioteca yfinance.
    """

    def extract_daily_data(
        self,
        symbols: List[str],
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Extrai dados diários de múltiplas ações.

        Args:
            symbols: Lista de códigos (ex: ['PETR4.SA', 'VALE3.SA', '^BVSP'])
            start_date: Data inicial
            end_date: Data final

        Returns:
            DataFrame consolidado com todos os símbolos
        """
        all_data = []

        for symbol in symbols:
            print(f"📊 Extraindo dados de {symbol}...")

            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(
                    start=start_date.strftime('%Y-%m-%d'),
                    end=end_date.strftime('%Y-%m-%d')
                )

                if not df.empty:
                    df = df.reset_index()
                    df['symbol'] = symbol
                    df['date'] = pd.to_datetime(
                        df['Date']
                        ).dt.strftime('%Y-%m-%d')

                    # Padroniza colunas
                    df = df.rename(columns={
                        'Open': 'open',
                        'High': 'high',
                        'Low': 'low',
                        'Close': 'close',
                        'Volume': 'volume'
                    })

                    df = df[
                        [
                            'date',
                            'symbol',
                            'open',
                            'high',
                            'low',
                            'close',
                            'volume'
                        ]
                    ]
                    all_data.append(df)
                    print(f"   ✓ {len(df)} registros extraídos")
                else:
                    print(f"   ⚠ Nenhum dado encontrado para {symbol}")

            except Exception as e:
                print(f"   ❌ Erro ao extrair {symbol}: {e}")
                continue

        if not all_data:
            raise ValueError(
                "Nenhum dado foi extraído para os símbolos fornecidos"
                )

        result = pd.concat(all_data, ignore_index=True)
        return result
