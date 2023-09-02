"""Unit tests for migration file service."""
import aiofiles.os
import pytest
from datetime import datetime, timezone
from pathlib import Path

from tests.conftest import use_temp_file  # noqa: F401
from py_db_migrate.service.migration_files import MigrationFiles


@pytest.fixture
def migration_files() -> MigrationFiles:
    return MigrationFiles()


class TestMigrationFiles:
    async def test_migration_files(self, migration_files, use_temp_file):
        folder_path = f"{use_temp_file}/migrations"
        await migration_files(folder_path=Path(folder_path), name="migration")

        files = await aiofiles.os.listdir(folder_path)
        assert any(["migration-up.sql" in file for file in files])
        assert any(["migration-down.sql" in file for file in files])

        with open(file=f"{folder_path}/{files[0]}", mode="r") as file:
            content = file.read()
        assert content == "/* Insert your SQL commands here. */"


class TestAddMigrationFiles:
    async def test_add_migration_files(self, migration_files, use_temp_file):
        await migration_files.add_migration_files(
            folder_path=Path(use_temp_file), name="migration"
        )

        result = await aiofiles.os.listdir(use_temp_file)
        assert set(result) == {"migration-up.sql", "migration-down.sql"}


class TestFormatFileNames:
    def test_format_file_names(self, migration_files):
        now = datetime.now(tz=timezone.utc)
        result = migration_files.format_file_names(name="test")
        # year
        assert str(now.year) == result[:4]
        # month
        assert str(now.isoformat()[5:7]) == result[4:6]
        # name
        assert "test" == result[-4:]


class TestCreateMigrationFolder:
    async def test_create_migration_folder(self, migration_files, use_temp_file):
        path = Path(f"{use_temp_file}/pymigrations")
        await migration_files.create_migration_folder(path=path)
        assert (await aiofiles.os.path.exists(path)) is True
