"""Database module."""

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from pydantic import (
    BaseModel,
    Field,
    validate_call,
)
from typing import Any


class Sql(ABC, BaseModel):
    """Sql class.

    Attributes:
        name: Database name.
        user: The user of the database.
        password: The password of the database.
        port: The port number to connect database
        host: The host of the database.

    Methods:
        fetch: Fetch a query.
        execute: Execute a query and don't return anything.
    """

    name: str
    user: str
    password: str
    port: int = Field(default=5432)
    host: str = Field(default="localhost")

    @abstractmethod
    @validate_call
    async def fetch(self, query: str) -> list[dict[str, Any]]:
        """Fetch a query.

        Arguments:
            query: Query to send to db.

        Returns:
            The response of the given query.
        """

    @abstractmethod
    @validate_call
    async def execute(self, query: str) -> None:
        """Execute a query.

        Arguments:
            query: Query to send to db.

        Returns:
            None.
        """

    @asynccontextmanager
    @abstractmethod
    @validate_call
    async def __call__(self):
        """Create a context manager.

        Returns:
            Connection to send queries to db.
        """
