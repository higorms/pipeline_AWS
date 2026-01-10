import pandas as pd
from pathlib import Path


def load_symbols(csv_path: str = None) -> list[str]:
    """Carrega a lista de símbolos a partir de um arquivo CSV.

    Args:
        csv_path (str, optional): Caminho para o arquivo CSV. Se None, usa o padrão 'resources/stocks.csv'.

    Returns:
        list[str]: Lista de símbolos carregados do CSV.
    """
    if csv_path is None:
        csv_path = Path(__file__).parent.parent / 'resources' / 'stocks.csv'

    df = pd.read_csv(csv_path)

    return df['acao'].tolist()