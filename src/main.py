"""Main file."""
import asyncio
from pathlib import Path
from src.service.start import Start
from src.service.migration_files import MigrationFiles


start = Start()
migration_files = MigrationFiles()


async def main():
    """Main function."""
    # await start(path=path)
    await migration_files(folder_path=Path("temp"), name="new_migration")


asyncio.run(main())
