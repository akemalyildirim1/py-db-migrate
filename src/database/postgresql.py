"""Postgresql class."""
from asyncpg import connect, Connection
from overrides import override
from pydantic import validate_call
from src.database import Sql
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
    def _get_connection_params(self) -> dict[str, str]:
        """Get connection parameters."""
        return self.model_dump()

    @validate_call
    async def _get_connection(self) -> Connection:
        """Get connection instance of database.

        Returns:
            Database connection.
        """
        return await connect(**self._get_connection_params())
