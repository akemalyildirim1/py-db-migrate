"""Shared service objects."""
from logging import Logger

from py_db_migrate.database import Sql
from py_db_migrate.logger import get_logger
from py_db_migrate.service import ServiceABC

logger = get_logger()


class Service(ServiceABC):
    """Service class.

    Attributes:
        logger: Logger object to follow process.
    """

    logger: Logger = logger


class SqlService(Service):
    """SqlService class.

    Attributes:
        database: Database object to connect db.
    """

    database: Sql
