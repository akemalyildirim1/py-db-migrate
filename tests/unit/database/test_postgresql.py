"""Unit tests for postgresql class."""
import pytest
from src.database.postgresql import PSql


@pytest.fixture
def psql() -> PSql:
    return PSql(
        user="admin",
        password="password",
        host="localhost",
        port="5432",
        database="postgres",
    )


class TestPsql:
    async def test_execute_and_fetch(self, psql):
        try:
            add_table_query = "create table name (id INT PRIMARY KEY, name TEXT)"
            await psql.execute(add_table_query)
            add_row_query = (
                "insert into name (id, name) values " "(1, 'test1')," "(2, 'test2')"
            )
            await psql.execute(add_row_query)
            result = await psql.fetch("select * from name")
            assert result == [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}]
        finally:
            await psql.execute("drop table name")


class TestPsqlHelpers:
    async def test_get_connection(self, psql):
        """
        Case: Check whether the program can connect to db or not.
        """
        await psql._get_connection()

    def test_get_connection_params(self, psql):
        result = psql._get_connection_params()

        assert result["host"] == "localhost"
        assert result["port"] == "5432"
        assert result["user"] == "admin"
        assert result["password"] == "password"
        assert result["database"] == "postgres"
