"""Shared service objects."""
from logging import Logger

from py_db_migrate.logger import get_logger
from py_db_migrate.service import ServiceABC

logger = get_logger()


class Service(ServiceABC):
    """Service class."""

    logger: Logger = logger
