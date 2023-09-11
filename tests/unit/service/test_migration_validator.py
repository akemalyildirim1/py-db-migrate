"""Unit tests for migration service."""
import pytest


from pathlib import Path

from tests.conftest import use_temp_file, psql  # noqa: F401
from tests.unit.service.test_migration_up import (  # noqa: F401
    create_and_delete_migration_table,
    migration_up,
)

from py_db_migrate.service import FolderNotFoundError, TableNotFoundError
from py_db_migrate.service.migration_validator import (
    MigrationTableAndFolderValidator,
)


@pytest.fixture
def migration_table_and_folder_validator(
    psql,
) -> MigrationTableAndFolderValidator:
    return MigrationTableAndFolderValidator(database=psql)


class TestMigrationTableAndFolderValidator:
    async def test_call(
        self,
        migration_table_and_folder_validator,
        create_and_delete_migration_table,
        use_temp_file,
    ):
        result = await migration_table_and_folder_validator(
            migration_folder=use_temp_file,
            migration_table=create_and_delete_migration_table,
        )
        assert result is None

    async def test_call_folder_not_found(
        self,
        migration_table_and_folder_validator,
    ):
        with pytest.raises(FolderNotFoundError):
            await migration_table_and_folder_validator(
                migration_folder=Path("./temp"), migration_table="table"
            )

    async def test_call_table_not_found(
        self, migration_table_and_folder_validator, use_temp_file
    ):
        with pytest.raises(TableNotFoundError):
            await migration_table_and_folder_validator(
                migration_folder=use_temp_file,
                migration_table="table",
            )
