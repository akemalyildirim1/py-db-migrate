"""Migration service module."""
from datetime import datetime, timezone
from pathlib import Path
from posix import DirEntry
from typing import Iterable

import aiofiles
import aiofiles.os

from asyncpg.exceptions import PostgresError
from pydantic import validate_call
from pypika import Query, Table

from py_db_migrate.service import (
    EmptyFileError,
    TableNotFoundError,
)
from py_db_migrate.service.migration_validator import (
    MigrationTableAndFolderValidator,
)
from py_db_migrate.service.service import SqlService


class MigrationError(ValueError):
    """Raises when there is a problem while running a migration."""


class MigrationUp(SqlService):
    """MigrationUp service class."""

    @validate_call
    async def __call__(self, migration_folder: Path, migration_table: str) -> None:
        """Run missing migrations.

        Firstly, check whether the migration folder exists or not. If it doesn't
        exist, raise an exception. Next, check whether the migration table exists
        or not. If it doesn't exist, create a table. Then, find the name of
        the migrated files from database and find the available migration files
        from the migration folder. Then, find the files that weren't migrated
        before and try to run them.

        Arguments:
            migration_folder: Migration folder path.
            migration_table: The name of the table that holds migrated files.

        Returns:
            None.

        Raises:
            FolderNotFoundError: If the migration folder couldn't be found.
            MigrationError: If the problem occurs while migrating.
        """
        validator: MigrationTableAndFolderValidator = MigrationTableAndFolderValidator(
            database=self.database
        )
        try:
            await validator(
                migration_folder=migration_folder,
                migration_table=migration_table,
            )

        except TableNotFoundError:
            await self.create_migration_table(name=migration_table)
            self.logger.info(f"Migration table:{migration_table} is created.")

        migrated_files_from_db: list[str] = await self.get_migrated_file_names_from_db(
            table=migration_table
        )

        migration_files_from_folder: tuple[
            str, ...
        ] = await self.get_existing_migration_files_from_migration_folder(
            folder=migration_folder
        )

        for migration_file_from_folder in migration_files_from_folder:
            if migration_file_from_folder in migrated_files_from_db:
                self.logger.info(f"{migration_file_from_folder} has been run before.")
                continue
            try:
                await self.migrate_file(
                    migration_folder=migration_folder,
                    migration_file=migration_file_from_folder,
                    migration_table=migration_table,
                )
                self.logger.info(f"{migration_file_from_folder} is running.")
            except (EmptyFileError, PostgresError) as e:
                raise MigrationError(
                    f"Problem occurred. Check {migration_file_from_folder}.\n"
                    f"`{str(e)}`"
                )

    @validate_call
    async def create_migration_table(self, name: str) -> None:
        """Create a table to store migrated files.

        Arguments:
            name: The name of the table.

        Returns:
            None.
        """
        await self.database.execute(  # nosec
            f"CREATE TABLE IF NOT EXISTS {name} ( "
            "date TIMESTAMP WITH TIME ZONE "
            "NOT NULL DEFAULT NOW(),"
            "name TEXT NOT NULL)"
        )

    @validate_call
    async def migrate_file(
        self, migration_folder: Path, migration_file: str, migration_table: str
    ) -> None:
        """Migrate the given file.

        Firstly, try to execute the given sql commands and then insert
        the information of this file to the migration table. Transaction
        is used for canceling if something goes wrong.

        Arguments:
            migration_folder: The path of the migration folder.
            migration_file: The name of the migration file.
            migration_table: The name of the migration table
                that we store migrated files in the db.

        Returns:
            None.

        Raise:
            EmptyFileError: When the file doesn't include any SQL command.
        """
        now: datetime = datetime.now(tz=timezone.utc)
        async with aiofiles.open(
            file=migration_folder / f"{migration_file}.sql",
            mode="r",
        ) as file:
            contents = await file.read()
            try:
                async with self.database() as connection:
                    await connection.execute(contents)
                    query = (
                        Query.into(Table(migration_table))
                        .columns("date", "name")
                        .insert(now, migration_file)
                    )
                    await connection.execute(str(query))

            except AttributeError as e:
                raise EmptyFileError from e

    @validate_call
    async def get_existing_migration_files_from_migration_folder(
        self, folder: Path
    ) -> tuple[str, ...]:
        """Get existing migration files after sorting..

        Arguments:
            folder: Folder to search existing migration files.

        Returns:
            The name of the existing migration files in the migration folder.

        Raises:
            FileNotFoundError: If there is no file.
        """
        entries: Iterable[DirEntry] = await aiofiles.os.scandir(path=folder)
        files: tuple[str, ...] = tuple(
            sorted(
                [
                    entry.name[:-4]
                    for entry in entries
                    if entry.is_file() and entry.name.endswith("-up.sql")
                ]
            )
        )
        if not files:
            self.logger.critical(f"There is no file found in {folder}.")
            raise FileNotFoundError
        return files

    @validate_call
    async def get_migrated_file_names_from_db(self, table: str) -> list[str]:
        """Get names of the migrated files from database.

        The results are ordered by time. The first one is the oldest one and
        the last one is the newest one.

        Arguments:
            table: The table name to search.

        Returns:
            The list of the names of migrated files.
        """
        query = Query.from_(Table(table)).select("name").orderby("date")

        query_result: list[dict[str, str]] = await self.database.fetch(str(query))

        return [row["name"] for row in query_result]
