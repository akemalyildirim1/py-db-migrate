"""Migration service module."""
import aiofiles
import aiofiles.os

from asyncpg.exceptions import PostgresError
from datetime import datetime, timezone
from pathlib import Path
from posix import DirEntry
from pydantic import validate_call
from pypika import Query, Table
from typing import Iterable

from py_db_migrate.service.service import SqlService
from py_db_migrate.service.utils import check_existence_of_file


class EmptyFileError(ValueError):
    """Raises when the given file is empty."""


class Migration(SqlService):
    """Migration service class."""

    @validate_call
    async def __call__(self, migration_folder: Path, migration_table: str) -> None:
        """Run main logic of the class.

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
        """
        if not (await check_existence_of_file(migration_folder)):
            self.logger.error(f"Migration folder {migration_folder} not found.")
            return

        migration_table = migration_table.replace("-", "_")

        if not (await self.check_existence_of_migration_table(name=migration_table)):
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
                self.logger.error(
                    f"Problem occurred. Check {migration_file_from_folder}.\n"
                    f"`{str(e)}`"
                )
                break

    @validate_call
    async def check_existence_of_migration_table(self, name: str) -> bool:
        """Check whether the migration table exists or not.

        Arguments:
            name: The name of the table to search.

        Returns:
            True if exists. Otherwise, False.
        """
        exist: bool = (  # nosec
            await self.database.fetch(
                "SELECT EXISTS (SELECT 1 "
                "FROM information_schema.tables "
                " WHERE table_schema = 'public' "
                f"AND table_name = '{name}' )"
            )
        )[0]["exists"]
        return exist

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
    async def get_migrated_file_names_from_db(self, table: str) -> list[str]:
        """Get names of the migrated files from database.

        Arguments:
            table: The table name to search.

        Returns:
            The list of the names of migrated files.
        """
        query = Query.from_(Table(table)).select("name")

        query_result: list[dict[str, str]] = await self.database.fetch(str(query))

        return [row["name"] for row in query_result]

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
