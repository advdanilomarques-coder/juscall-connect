"""Structured-ish logging setup shared across the app."""
import logging
import sys

_configured = False


def setup_logging(level: str = "INFO") -> None:
    global _configured
    if _configured:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s", datefmt="%H:%M:%S")
    )
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]
    _configured = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
