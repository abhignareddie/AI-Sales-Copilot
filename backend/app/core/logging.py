import logging
import sys
from app.core.config import settings


def setup_logging() -> logging.Logger:
    _logger = logging.getLogger(settings.APP_NAME)
    _logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    if not _logger.handlers:
        _logger.addHandler(handler)

    return _logger


logger = setup_logging()
