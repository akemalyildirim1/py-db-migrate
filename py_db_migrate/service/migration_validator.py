"""Migration service module."""
from pathlib import Path

from pydantic import validate_call

from py_db_migrate.service import FolderNotFoundError, TableNotFoundError
from py_db_migrate.service.service import SqlService
from py_db_migrate.service.utils import check_existence_of_file


class MigrationTableAndFolderValidator(SqlService):
    """MigrationTableAndFolderValidator class."""

    async def __call__(self, migration_folder: Path, migration_table: str) -> None:
        """Validate the migration table and folder.

        Firstly, check whether the migration folder exists or not. Then,
        check whether the migration table exists or not.

        Arguments:
            migration_folder: Migration folder path.
            migration_table: The name of the table that holds migrated files.

        Returns:
            None.

        Raises:
            FolderNotFoundError: If the migration folder couldn't be found.
            TableNotFoundError: If the migration table couldn't be found.
        """
        if not (await check_existence_of_file(migration_folder)):
            raise FolderNotFoundError(
                f"Migration folder {migration_folder} couldn't be found."
            )

        migration_table = migration_table.replace("-", "_")

        if not (await self.check_existence_of_migration_table(name=migration_table)):
            raise TableNotFoundError(
                f"Migration table {migration_table} couldn't be found."
            )

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
