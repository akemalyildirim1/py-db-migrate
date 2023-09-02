"""Utils functions of the service layer."""
import aiofiles.os

from pathlib import Path
from pydantic import validate_call


@validate_call
async def check_existence_of_file(path: Path) -> bool:
    """Check whether the given file exists or not.

    Arguments:
        path: Path of the file to search.

    Returns:
        True if file exists. Otherwise, False.
    """
    return await aiofiles.os.path.exists(path)
