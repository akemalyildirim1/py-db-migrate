"""Main file."""
import asyncio
import typer

from pathlib import Path
from typing_extensions import Annotated

from py_db_migrate.configuration import Configuration, get_configuration
from py_db_migrate.service.start import Start
from py_db_migrate.service.migration_files import MigrationFiles

app = typer.Typer(help="Awesome CLI user manager.")

CONFIGURATION_FILE_PATH = Path("./py-db-migration.yaml")


@app.command("init")
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


#
# @app.command()
# def delete(
#     username: str,
#     force: bool = typer.Option(
#         ...,
#         prompt="Are you sure you want to delete the user?",
#         help="Force deletion without confirmation.",
#     ),
# ):
#     """
#     Delete a user with USERNAME.
#
#     If --force is not used, will ask for confirmation.
#     """
#     if force:
#         print(f"Deleting user: {username}")
#     else:
#         print("Operation cancelled")
#
#
# @app.command()
# def delete_all(
#     force: bool = typer.Option(
#         ...,
#         prompt="Are you sure you want to delete ALL users?",
#         help="Force deletion without confirmation.",
#     )
# ):
#     """
#     Delete ALL users in the database.
#
#     If --force is not used, will ask for confirmation.
#     """
#     if force:
#         print("Deleting all users")
#     else:
#         print("Operation cancelled")
#
#
# @app.command()
# def init():
#     """
#     Initialize the users database.
#     """
#     print("Initializing user database")


if __name__ == "__main__":
    app()
