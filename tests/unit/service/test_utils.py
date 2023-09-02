"""Unit tests for util functions of service layer."""
import aiofiles.os
from pathlib import Path

from tests.conftest import use_temp_file  # noqa: F401

from py_db_migrate.service.utils import check_existence_of_file


class TestCheckExistenceOfFile:
    async def test_check_existence_of_file_true(self, use_temp_file):
        path = Path(f"{use_temp_file}/config.yaml")
        async with aiofiles.open(path, mode="w") as file:
            await file.write("test")
        result = await check_existence_of_file(path)
        assert result is True

    async def test_check_existence_of_file_false(self):
        result = await check_existence_of_file(Path("temp/config.yaml"))
        assert result is False
