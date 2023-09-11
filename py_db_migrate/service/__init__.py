"""Service module."""
from abc import ABC

from pydantic import BaseModel, ConfigDict


class ServiceABC(ABC, BaseModel):
    """ServiceABC class."""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class EmptyFileError(ValueError):
    """Raises when the given file is empty."""


class TableNotFoundError(ValueError):
    """Raises when the migration table couldn't be found."""


class FolderNotFoundError(ValueError):
    """Raises when the folder couldn't be found."""
