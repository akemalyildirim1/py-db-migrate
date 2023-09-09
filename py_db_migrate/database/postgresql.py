"""Postgresql class."""
from asyncpg import connect, Connection
from contextlib import asynccontextmanager
from overrides import override
from pydantic import validate_call
from py_db_migrate.database import Sql
from typing import Any


class PSql(Sql):
    """Psql class."""

    @override
    async def fetch(self, query: str) -> list[dict[str, Any]]:
        """Fetch a query."""
        connection: Connection = await self._get_connection()
        query_result = await connection.fetch(query)
        return [dict(row) for row in query_result]

    @override
    async def execute(self, query: str) -> None:
        """Execute a query."""
        connection: Connection = await self._get_connection()
        await connection.execute(query)

    # Helpers.
    @validate_call
    def _get_connection_params(self) -> dict[str, str | int]:
        """Get connection parameters."""
        params: dict[str, str | int] = self.model_dump()
        params["database"] = params["name"]
        del params["name"]
        return params

    @validate_call
    async def _get_connection(self) -> Connection:
        """Get connection instance of database.

        Returns:
            Database connection.
        """
        return await connect(**(self._get_connection_params()))

    @asynccontextmanager
    @override
    async def __call__(self) -> Connection:
        """Create a context manager and return connection.

        Returns:
            A database connection.
        """
        connection: Connection = await self._get_connection()
        async with connection.transaction():
            yield connection
