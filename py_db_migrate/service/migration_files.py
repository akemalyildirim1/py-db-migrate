"""Migration files service."""
import aiofiles.os
from aiofiles import open
from datetime import datetime, timezone
from pathlib import Path
from pydantic import validate_call


from py_db_migrate.service.utils import check_existence_of_file
from py_db_migrate.service.service import Service


class MigrationFiles(Service):
    """MigrationFiles class."""

    @validate_call
    async def __call__(self, folder_path: Path, name: str) -> None:
        """Run the main logic of the class.

        After finding the formatted name, insert two sql files by adding
        `-up.sql` and `-down.sql` names to the given folder.

        Arguments:
            folder_path: Folder to add new files.
            name: Name of the migration files to create.

        Returns:
            None.
        """
        formatted_name: str = self.format_file_names(name=name)

        if not (await check_existence_of_file(path=folder_path)):
            await self.create_migration_folder(path=folder_path)
            self.logger.info(f"{folder_path} folder is created.")

        await self.add_migration_files(folder_path=folder_path, name=formatted_name)
        self.logger.info("New migration files are added.")

    @staticmethod
    @validate_call
    async def add_migration_files(folder_path: Path, name: str) -> None:
        """Add migration files to the given folder.

        Arguments:
            folder_path: Folder to add new files.
            name: Name of the migration files to create.

        Returns:
            None.
        """
        for new_file_name in (f"{name}-up.sql", f"{name}-down.sql"):
            async with open(file=folder_path.joinpath(new_file_name), mode="w") as file:
                await file.write("/* Insert your SQL commands here. */")

    @staticmethod
    @validate_call
    def format_file_names(name: str) -> str:
        """Format the given name to the project format.

        Arguments:
            name: Desired name.

        Returns:
            The formatted name. (YYYYMMDDmmss-{name})
        """
        now: datetime = datetime.now(tz=timezone.utc)
        formatted_datetime = now.strftime("%Y%m%d%H%M%S")
        return f"{formatted_datetime}-{name}"

    @staticmethod
    @validate_call
    async def create_migration_folder(path: Path) -> None:
        """Create a folder to store migration files.

        Arguments:
            path: Path of the new folder.

        Returns:
            None.
        """
        await aiofiles.os.mkdir(path=path, mode=0o755)
