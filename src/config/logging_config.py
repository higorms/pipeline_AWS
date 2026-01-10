"""
Configuração centralizada de logging para o projeto.
"""
import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_format: Optional[str] = None,
    include_timestamp: bool = True
) -> None:
    """
    Configura o sistema de logging da aplicação.

    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Formato customizado do log (opcional)
        include_timestamp: Se deve incluir timestamp nos logs
    """
    if log_format is None:
        if include_timestamp:
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        else:
            log_format = '%(name)s - %(levelname)s - %(message)s'

    # Converte string para nível de logging
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configura logging básico
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True  # Sobrescreve configurações anteriores
    )

    # Reduz verbosidade de bibliotecas externas
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('yfinance').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger configurado para o módulo especificado.

    Args:
        name: Nome do módulo (geralmente __name__)

    Returns:
        Logger configurado
    """
    return logging.getLogger(name)
