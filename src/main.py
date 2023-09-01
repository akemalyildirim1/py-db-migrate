"""Main file."""
import asyncio
from src.service.start import Start

start = Start()


async def main(path):
    """Main function."""
    await start(path=path)


asyncio.run(main("pydbmigrations.yaml"))
