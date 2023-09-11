"""Migration down service module."""
from pathlib import Path

import aiofiles
import aiofiles.os
from pydantic import validate_call
from pypika import Order, Query, Table

from py_db_migrate.service import EmptyFileError
from py_db_migrate.service.migration_validator import (
    MigrationTableAndFolderValidator,
)
from py_db_migrate.service.service import SqlService
from py_db_migrate.service.utils import check_existence_of_file


class EmptyTableError(ValueError):
    """Raises when the given database table is empty."""


class MigrationDown(SqlService):
    """Migration service class."""

    @validate_call
    async def __call__(self, migration_folder: Path, migration_table: str) -> None:
        """Delete the latest migration.

        Firstly, check whether the migration folder and migration table
        exist or not. If one of them doesn't exist, raise an exception.
        Then, find the name of the down version of the latest migrated file to
        database. Lastly, run the down migration file and delete the name of
        the latest migrated file from the migration table.

        Arguments:
            migration_folder: Migration folder path.
            migration_table: The name of the table that holds migrated files.

        Returns:
            None.

        Raises:
            FolderNotFoundError: If the migration folder doesn't exist.
            TableNotFoundError: If the migration table doesn't exist.
            EmptyTableError: If the migration table is empty.
            FileNotFound: If the down file of the latest migrated
                file doesn't exist in the migration folder.
        """
        validator: MigrationTableAndFolderValidator = MigrationTableAndFolderValidator(
            database=self.database
        )

        await validator(
            migration_folder=migration_folder,
            migration_table=migration_table,
        )

        migration_down_file: str = (
            await self._get_down_file_of_the_latest_migrated_file(
                migration_table=migration_table
            )
        )

        if not (
            await check_existence_of_file(
                migration_folder / f"{migration_down_file}.sql"
            )
        ):
            raise FileNotFoundError(f"{migration_down_file} couldn't be found.")

        await self.migrate_down(
            migration_folder=migration_folder,
            migration_file=migration_down_file,
            migration_table=migration_table,
        )
        self.logger.info(f"{migration_down_file} is running.")

    @validate_call
    async def _get_down_file_of_the_latest_migrated_file(
        self, migration_table: str
    ) -> str:
        """Search for the down version of the latest migrated file.

        Arguments:
            migration_table: Migration table to search.

        Returns:
            The name of the down file of the latest migrated file.

        Raises:
            EmptyTableError: If the migration table doesn't have any row.
        """
        table: Table = Table(migration_table)
        query_result: list[dict[str, str]] = await self.database.fetch(
            str(
                Query.from_(table)
                .select("name")
                .orderby("date", order=Order.desc)
                .limit(1)
            )
        )

        if not query_result:
            raise EmptyTableError(
                f"There is no migrated file found in migration table {migration_table}"
            )

        latest_migrated_file: str = query_result[0]["name"]
        return latest_migrated_file[:-3] + "-down"

    @validate_call
    async def migrate_down(
        self, migration_folder: Path, migration_file: str, migration_table: str
    ) -> None:
        """Down the migration of the given file.

        Firstly, try to execute the given -down.sql commands and then delete
        the name of the latest migrated file from migration table. Transaction
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
        migration_tb: Table = Table(migration_table)
        async with aiofiles.open(
            file=migration_folder / f"{migration_file}.sql",
            mode="r",
        ) as file:
            contents = await file.read()
            try:
                async with self.database() as connection:
                    await connection.execute(contents)
                    query = (
                        Query.from_(migration_tb)
                        .delete()
                        .where(migration_tb.name == f"{migration_file[:-4]}up")
                    )
                    await connection.execute(str(query))
            except AttributeError as e:
                raise EmptyFileError from e
