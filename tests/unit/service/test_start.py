"""Unit tests for start service."""
import aiofiles.os
import pytest
import yaml
from pathlib import Path

from tests.conftest import use_temp_file  # noqa: F401
from py_db_migrate.service.start import Start


@pytest.fixture
def start_service() -> Start:
    return Start()


class TestStart:
    async def test_start_new_config(self, start_service, use_temp_file):
        """
        Case: Config file doesn't exist. Create a new one.
        """
        path = Path(f"{use_temp_file}/config.yaml")
        await start_service(path)

        with open(path, mode="r") as file:
            content = yaml.load(file, Loader=yaml.FullLoader)

        assert all([key in content for key in ("database", "migration_directory")])

    async def test_start_existing(self, start_service, use_temp_file):
        """
        Case: Config file exists. Do not do anything.
        """
        path = Path(f"{use_temp_file}/config.yaml")

        async with aiofiles.open(path, mode="w") as file:
            await file.write("test")
        await start_service(path)

        async with aiofiles.open(path, mode="r") as file:
            content = await file.read()

        assert content == "test"


class TestCreateConfigurationFile:
    async def test_create_configuration_file(self, start_service, use_temp_file):
        path = Path(f"{use_temp_file}/config.yaml")
        start_service.create_configuration_file(path)

        with open(path, mode="r") as file:
            content = yaml.load(file, Loader=yaml.FullLoader)

        assert content["database"] == {
            "host": "localhost",
            "port": 5432,
            "user": "your_db_username",
            "password": "your_db_password",
            "name": "your_db_name",
        }
        assert content["migration_directory"] == "pydbmigrations"
