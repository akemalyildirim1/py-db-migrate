"""Configuration related objects."""
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ValidationError

from py_db_migrate.logger import get_logger

logger = get_logger()


class DatabaseFields(BaseModel):
    """DatabaseFields model."""

    host: str
    name: str
    password: str
    port: int
    user: str


class Configuration(BaseModel):
    """Configuration model."""

    database: DatabaseFields
    migration_directory: str


@lru_cache(maxsize=1)
def get_configuration(path: Path) -> Configuration:
    """Read and check the py-db-migration.yaml file.

    Returns:
        Configuration file of the project.
    """
    logger.info("Reading configuration file...")
    try:
        config_data: dict[str, Any]
        with open(path, "r") as yaml_file:
            config_data = yaml.safe_load(yaml_file)

        configuration: Configuration = Configuration(
            database=DatabaseFields(**config_data["database"]),
            migration_directory=config_data["migration_directory"],
        )
        logger.info("Configuration file is ready.")
        return configuration
    except (ValidationError, KeyError, TypeError):
        logger.error("Configuration file is incorrect.")
    except FileNotFoundError:
        logger.error("Configuration file couldn't be found.")
    sys.exit(1)
