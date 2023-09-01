"""Shared service objects."""
from logging import Logger

from src.logger import get_logger
from src.service import ServiceABC

logger = get_logger()


class Service(ServiceABC):
    """Service class."""

    logger: Logger = logger
