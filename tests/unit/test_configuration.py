"""Unit tests for configuration."""
import aiofiles.os
import pytest
from pathlib import Path

from tests.conftest import use_temp_file  # noqa: F401
from tests.unit.service.test_start import start_service  # noqa: F401

from py_db_migrate.configuration import (
    get_configuration,
    DatabaseFields,
    Configuration,
)


class TestGetConfiguration:
    async def test_get_configuration(self, start_service, use_temp_file):
        path = Path(f"{use_temp_file}/py-db-migration.yaml")
        await start_service(path)
        result = get_configuration(path)

        assert result == Configuration(
            database=DatabaseFields(
                host="localhost",
                port=5432,
                user="your_db_username",
                password="your_db_password",
                name="your_db_name",
            ),
            migration_directory="pydbmigrations",
        )

    async def test_get_configuration_no_config_file(self):
        """
        Case: There is no configuration file.
        """
        path = Path("./temp/py-db-migration.yaml")

        with pytest.raises(SystemExit):
            get_configuration(path)

    async def test_get_configuration_wrong_config_file(self, use_temp_file):
        """
        Case: Configuration file is incorrect.
        """
        async with aiofiles.open(
            file=f"{use_temp_file}/py-db-migration.yaml", mode="w"
        ) as file:
            await file.write("test")

        path = Path(f"{use_temp_file}/py-db-migration.yaml")

        with pytest.raises(SystemExit):
            get_configuration(path)
