"""Start Service."""
import yaml
import aiofiles.os
from pathlib import Path
from pydantic import validate_call
from src.service.service import Service


class Start(Service):
    """Start class."""

    @validate_call
    async def __call__(self, path: Path) -> None:
        """Run main logic of the class.

        Firstly, check for the configuration file, if it doesn't
        exist, create it by using default fields.

        Arguments:
            path: Path to check and create config file if needed.

        Returns:
            None.
        """
        is_file_exist: bool = await self.check_existence_of_file(path=path)

        if is_file_exist:
            self.logger.warning("Configuration file already existed.")
            return None

        self.create_configuration_file(path=path)
        self.logger.info("Configuration file is created.")

    @staticmethod
    @validate_call
    async def check_existence_of_file(path: Path) -> bool:
        """Check whether the given file exists or not.

        Arguments:
            path: Path of the file to search.

        Returns:
            True if file exists. Otherwise, False.
        """
        return await aiofiles.os.path.exists(path)

    @staticmethod
    @validate_call
    def create_configuration_file(path: Path) -> None:
        """Create a configuration file.

        Arguments:
            path: Path to create a file.

        Returns:
            None.
        """
        default_configurations: dict[str, str | dict[str, int | str]] = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "user": "your_db_username",
                "password": "your_db_password",
                "name": "your_db_name",
            },
            "migration_directory": "pydbmigrations",
        }
        with open(path, mode="w") as file:
            yaml.dump(default_configurations, file, default_flow_style=False)
