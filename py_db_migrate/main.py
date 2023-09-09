"""Main file."""
import asyncio
import typer

from pathlib import Path
from typing_extensions import Annotated

from py_db_migrate.configuration import Configuration, get_configuration
from py_db_migrate.database.postgresql import PSql
from py_db_migrate.logger import get_logger
from py_db_migrate.service.start import Start
from py_db_migrate.service.migration_files import MigrationFiles
from py_db_migrate.service.migration import Migration

app = typer.Typer(help="Awesome CLI user manager.")

CONFIGURATION_FILE_PATH = Path("./py-db-migration.yaml")

logger = get_logger()


@app.command("init")
@app.command("start")
def start():
    """Create an initial configuration file.

    You need to update this configuration file.
    """
    start_service: Start = Start()
    asyncio.run(start_service(path=CONFIGURATION_FILE_PATH))


@app.command("create")
def create(name: Annotated[str, typer.Argument(help="Name of the SQL files.")]):
    """Create a new sql file."""
    migration_files: MigrationFiles = MigrationFiles()
    configuration: Configuration = get_configuration(path=CONFIGURATION_FILE_PATH)
    asyncio.run(
        migration_files(folder_path=Path(configuration.migration_directory), name=name)
    )


@app.command("up")
def migration_up():
    """Run the new migration files."""
    configuration: Configuration = get_configuration(path=CONFIGURATION_FILE_PATH)
    psql: PSql = PSql(**(configuration.database.model_dump()))

    migration: Migration = Migration(database=psql)
    try:
        asyncio.run(
            migration(
                migration_folder=Path(configuration.migration_directory),
                migration_table="pydbmigration",
            )
        )
    except Exception as e:
        logger.critical(str(e))


if __name__ == "__main__":
    app()
