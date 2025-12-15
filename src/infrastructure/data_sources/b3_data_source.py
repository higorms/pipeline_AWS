"""
Implementação da extração de dados via scraping (placeholder para implementação futura).
Esta classe pode ser implementada usando BeautifulSoup, Selenium ou outras ferramentas
para fazer scraping direto do site da B3 ou outros portais financeiros.
"""
from datetime import date
from typing import List
import pandas as pd

from domain.repositories.data_source_repository import DataSourceRepository


class B3DataSource(DataSourceRepository):
    """
    Extrai dados da B3 via web scraping.
    
    NOTA: Esta é uma implementação placeholder.
    Para uso em produção, implemente o scraping usando:
    - BeautifulSoup4
    - Selenium
    - Scrapy
    
    Considere também:
    - Rate limiting
    - Respeito ao robots.txt
    - Headers apropriados
    - Tratamento de erros HTTP
    """

    def extract_daily_data(
        self,
        symbols: List[str],
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Extrai dados diários via scraping.
        
        Args:
            symbols: Lista de códigos das ações
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            DataFrame com dados extraídos
            
        Raises:
            NotImplementedError: Esta implementação ainda não está disponível
        """
        raise NotImplementedError(
            "B3DataSource ainda não implementado. "
            "Use YFinanceDataSource como alternativa ou implemente o scraping aqui."
        )
