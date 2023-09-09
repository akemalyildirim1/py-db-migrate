"""Unit tests for migration service."""
import aiofiles.os
import pytest


from contextlib import asynccontextmanager
from uuid import uuid4
from pathlib import Path

from tests.conftest import use_temp_file, psql  # noqa: F401
from py_db_migrate.service.migration import Migration, EmptyFileError


@pytest.fixture
def migration(psql) -> Migration:
    return Migration(database=psql)


@asynccontextmanager
async def create_and_delete_migration_table(migration: Migration, table_name: str):
    try:
        await migration.create_migration_table(table_name)
        yield
    finally:
        await migration.database.execute(f"drop table {table_name}")


class TestMigration:
    async def test_migration_file(self, migration, use_temp_file):
        try:
            # Create dummy table for testing whether the files
            # are migrated or not.
            await migration.database.execute(
                "create table check_migration (id SERIAL PRIMARY KEY, " "name text) "
            )

            # Create dummy migration files.
            for file_name in (
                "20230902182613-file-1-up",
                "20230802182613-file-2-up",
                "20231002182613-file-3-up",
                "20220902182613-file-4-up",
            ):
                table_name = file_name.replace("-", "_")
                async with aiofiles.open(
                    Path(f"{use_temp_file}/{file_name}.sql"),
                    mode="w",
                ) as file:
                    await file.write(
                        "insert into check_migration (name) "
                        f"values ('{file_name}'); "
                    )

            table_name = "pydbmigration"
            async with create_and_delete_migration_table(migration, table_name):
                # File 1 is added to pydbmigration and
                # it should't be run again.
                await migration.database.execute(
                    "insert into pydbmigration (date, name )"
                    "values (now(),'20230902182613-file-1-up')"
                )

                await migration(
                    migration_folder=Path(use_temp_file),
                    migration_table="pydbmigration",
                )

                # This query result should be empty since
                # file 1 shouldn't be migrated again.
                check_query_file_1 = await migration.database.fetch(
                    "select id from check_migration "
                    "where name ='20230902182613-file-1-up' "
                )

                check_query_migrated_files = await migration.database.fetch(
                    "select id,name from check_migration "
                )

                check_query_migration_file = await migration.database.fetch(
                    "select name from pydbmigration"
                )

                assert not check_query_file_1

                assert len(check_query_migrated_files) == 3
                assert all(
                    [
                        "20230902182613-file-1-up" not in row["name"]
                        for row in check_query_migrated_files
                    ]
                )

                assert len(check_query_migration_file) == 4

        finally:
            await migration.database.execute("drop table check_migration")

    async def test_migration_file_no_migration_table_before(
        self, migration, use_temp_file
    ):
        """
        Case: There is no migration file and function should generate it.
        """
        try:
            file_name = "20230902182613-file-1-up"
            migration_table_name = "pydbmigration_nomigrationtable"
            async with aiofiles.open(
                Path(f"{use_temp_file}/{file_name}.sql"),
                mode="w",
            ) as file:
                await file.write("create table testtest (id int primary key);")

            await migration(
                migration_folder=Path(use_temp_file),
                migration_table=migration_table_name,
            )

            [check_query_migration_table] = await migration.database.fetch(
                f"select date from {migration_table_name} "
                "where name ='20230902182613-file-1-up' "
            )

            assert check_query_migration_table["date"] is not None

        finally:
            await migration.database.execute(f"drop table {migration_table_name}")
            await migration.database.execute("drop table testtest")

    async def test_migration_file_syntax_error(self, migration, use_temp_file):
        """
        Case: There is a syntax error in migration file.
        """
        table_name = "pydbmigration_syntaxerror"
        file_name = "20230902182613-file-1-up"
        async with aiofiles.open(
            Path(f"{use_temp_file}/{file_name}.sql"),
            mode="w",
        ) as file:
            await file.write("create table testtest (id int pri")

        async with create_and_delete_migration_table(migration, table_name):
            await migration(
                migration_folder=Path(use_temp_file),
                migration_table=table_name,
            )

            check_query_migration_table = await migration.database.fetch(
                f"select date from {table_name} " f"where name ='{file_name}' "
            )

            assert not check_query_migration_table

    async def test_migration_file_not_found(self, migration):
        """
        Case: The given migration folder doesn't exist. The program will return
            directly.
        """
        await migration(migration_folder=Path("./temp"), migration_table="table")


class TestCheckExistenceOfMigrationTable:
    async def test_check_existence_of_migration_table_false(self, migration):
        result = await migration.check_existence_of_migration_table("test")
        assert result is False

    async def test_check_existence_of_migration_table_true(self, migration):
        migration_table_name = f"test_{str(uuid4()).replace('-', '_')}"
        try:
            await migration.database.execute(
                f"create table {migration_table_name} (id int)"
            )
            result = await migration.check_existence_of_migration_table(
                migration_table_name
            )
            assert result is True
        finally:
            await migration.database.execute(f"drop table {migration_table_name}")


class TestCreateMigrationTable:
    async def test_create_migration_table(self, migration):
        table_name = "new_create_migration_table"
        async with create_and_delete_migration_table(migration, table_name):
            result = await migration.check_existence_of_migration_table(table_name)
            assert result is True


class TestGetMigratedFileNamesFromDatabase:
    async def test_get_migrated_file_names(self, migration):
        table_name = "test_get_migrated_file_name"
        async with create_and_delete_migration_table(migration, table_name):
            await migration.database.execute(
                f"insert into {table_name} (date, name) values "
                "('2021-09-23T01:00:00Z', 'file1-up'),"
                "('2022-09-23T01:00:00Z', 'file2-up'),"
                "('2023-09-23T01:00:00Z', 'file3-up')"
            )
            result = await migration.get_migrated_file_names_from_db(table=table_name)

            assert len(result) == 3
            assert result == ["file1-up", "file2-up", "file3-up"]

    async def test_get_migrated_file_names_no_file(self, migration):
        table_name = "test_get_migrated_file_name_no_file"
        try:
            await migration.create_migration_table(table_name)
            result = await migration.get_migrated_file_names_from_db(table=table_name)
            assert len(result) == 0
            assert result == []
        finally:
            await migration.database.execute(f"drop table {table_name}")


class TestGetExistingMigrationFilesFromMigrationFolder:
    async def test_get_existing_migration_files_from_migration_folder(
        self, migration, use_temp_file
    ):
        for file_name in (
            "20230902182613-file-1-up",
            "20230802182613-file-2-up",
            "20231002182613-file-3-up",
            "20220902182613-file-4-up",
            "20220902182613-file-4-down",
        ):
            pass
            async with aiofiles.open(
                Path(f"{use_temp_file}/{file_name}.sql"),
                mode="w",
            ) as file:
                await file.write("/* testing */")

        result = await migration.get_existing_migration_files_from_migration_folder(
            Path(use_temp_file)
        )

        assert len(result) == 4
        assert result == (
            "20220902182613-file-4-up",
            "20230802182613-file-2-up",
            "20230902182613-file-1-up",
            "20231002182613-file-3-up",
        )

    async def test_get_existing_migration_files_from_migration_folder_empty(
        self, migration, use_temp_file
    ):
        """
        Case: Migration folder is empty.
        """
        with pytest.raises(FileNotFoundError):
            await migration.get_existing_migration_files_from_migration_folder(
                Path(use_temp_file)
            )


class TestMigrateFile:
    async def test_migrate_file(self, migration, use_temp_file):
        file_name = "20231002182613-file-3-up"
        new_table_name = "testmigratefile"
        try:
            async with aiofiles.open(
                Path(f"{use_temp_file}/{file_name}.sql"),
                mode="w",
            ) as file:
                await file.write(
                    f"create table {new_table_name} (id int PRIMARY KEY);"
                    f"insert into {new_table_name} (id) values (1), (2);"
                )

            table_name = "new_migration_table"
            async with create_and_delete_migration_table(migration, table_name):
                await migration.migrate_file(
                    migration_folder=use_temp_file,
                    migration_file=file_name,
                    migration_table=table_name,
                )

                check_query = await migration.database.fetch(
                    f"select * from {new_table_name}"
                )

                [check_migration_table_query] = await migration.database.fetch(
                    f"select name from {table_name}"
                )

            assert len(check_query) == 2
            assert all([element in [{"id": 1}, {"id": 2}] for element in check_query])
            assert check_migration_table_query["name"] == file_name

        finally:
            await migration.database.execute(f"drop table {new_table_name}")

    async def test_migrate_file_empty_file(self, migration, use_temp_file):
        """
        Case: Given file is empty. So, it will raise Empty file error.
        """
        file_name = "20231002182613-file-1-up"
        async with aiofiles.open(
            Path(f"{use_temp_file}/{file_name}.sql"),
            mode="w",
        ) as file:
            await file.write("/* random comments */ ")

        with pytest.raises(EmptyFileError):
            await migration.migrate_file(
                migration_folder=use_temp_file,
                migration_file=file_name,
                migration_table="testmigratefileemptyfile",
            )
