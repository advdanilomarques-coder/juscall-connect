"""Configuração de logs estruturados.

Um sistema comercial precisa de logs claros para auditoria, depuração e
monitoramento. Aqui centralizamos a configuração para que todo o projeto
use o mesmo formato de log.
"""

from __future__ import annotations

import logging

from app.core.config import settings


def setup_logging() -> None:
    """Configura o logger raiz uma única vez, no início da aplicação."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger nomeado para o módulo que o solicita.

    Uso típico:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("mensagem")
    """
    return logging.getLogger(name)
