"""Unit tests for migration down service."""
import aiofiles.os
import pytest


from pathlib import Path

from tests.conftest import use_temp_file, psql  # noqa: F401
from tests.unit.service.test_migration_up import (  # noqa: F401
    create_and_delete_migration_table,
    migration_up,
)

from py_db_migrate.service import EmptyFileError
from py_db_migrate.service.migration_down import MigrationDown, EmptyTableError


@pytest.fixture
def migration_down(psql) -> MigrationDown:
    return MigrationDown(database=psql)


class TestMigrationDown:
    async def test_call(
        self, migration_down, use_temp_file, create_and_delete_migration_table
    ):
        file_name = "file3-down"
        new_table_name = "testmigrationdown"
        table_name = create_and_delete_migration_table  # migration table

        await migration_down.database.execute(
            f"insert into {table_name} (name, date) values "
            "('file2-up','2020-01-03T01:00:00Z'),"
            "('file3-up','2021-01-03T01:00:00Z')"
        )

        async with aiofiles.open(
            Path(f"{use_temp_file}/{file_name}.sql"),
            mode="w",
        ) as file:
            await file.write(
                f"create table {new_table_name} (id int PRIMARY KEY);"
                f"insert into {new_table_name} (id) values (1), (2);"
            )

        try:
            await migration_down(
                migration_folder=use_temp_file,
                migration_table=table_name,
            )

            check_query = await migration_down.database.fetch(
                f"select * from {new_table_name}"
            )

            check_migration_table_query = await migration_down.database.fetch(
                f"select name from {table_name}"
            )

            assert len(check_query) == 2
            assert all([element in [{"id": 1}, {"id": 2}] for element in check_query])

            assert len(check_migration_table_query) == 1
            assert check_migration_table_query[0]["name"] == "file2-up"
        finally:
            await migration_down.database.execute(f"drop table {new_table_name}")

    async def test_call_down_file_not_found(
        self, migration_down, use_temp_file, create_and_delete_migration_table
    ):
        """
        Case: There is no down file. It will raise FileNotFoundError.
        """
        table_name = create_and_delete_migration_table
        await migration_down.database.execute(
            f"insert into {table_name} (name, date) values "
            "('migratefile-up','2021-01-03T01:00:00Z')"
        )
        with pytest.raises(FileNotFoundError):
            await migration_down(
                migration_folder=Path(use_temp_file),
                migration_table=table_name,
            )


class TestGetDownFileOfTheLatestMigratedFile:
    async def test_get_down_file_of_the_latest_migrated_file(
        self, migration_down, create_and_delete_migration_table
    ):
        table_name = create_and_delete_migration_table
        await migration_down.database.execute(
            f"insert into {table_name} (name, date) values "
            "('firstmigratedfile-up','2022-01-03T01:00:00Z'),"
            "('lastmigratedfile-up', now())"
        )
        result = await migration_down._get_down_file_of_the_latest_migrated_file(
            migration_table=table_name
        )

        assert result == "lastmigratedfile-down"

    async def test_get_down_file_of_the_latest_migrated_file_empty_table(
        self, migration_down, create_and_delete_migration_table
    ):
        """
        Case: Migration table is empty.
        """
        table_name = create_and_delete_migration_table
        with pytest.raises(EmptyTableError):
            await migration_down._get_down_file_of_the_latest_migrated_file(
                migration_table=table_name
            )


class TestMigrateDown:
    async def test_migrate_down_empty_file_error(
        self, migration_down, use_temp_file, create_and_delete_migration_table
    ):
        """
        Case: Given file is empty. So, it will raise Empty file error.
        """
        table_name = create_and_delete_migration_table  # migration table
        file_name = "20230923182613-file-1-down"

        await migration_down.database.execute(
            f"insert into {table_name} (name, date) values "
            "('20230923182613-file-1-up','2021-01-03T01:00:00Z')"
        )

        async with aiofiles.open(
            Path(f"{use_temp_file}/{file_name}.sql"),
            mode="w",
        ) as file:
            await file.write("/* random comments */ ")

        with pytest.raises(EmptyFileError):
            await migration_down.migrate_down(
                migration_folder=use_temp_file,
                migration_file=file_name,
                migration_table=table_name,
            )
