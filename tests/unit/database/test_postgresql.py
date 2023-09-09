"""Unit tests for postgresql class."""
from tests.conftest import psql  # noqa: F401


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
            assert result == [
                {"id": 1, "name": "test1"},
                {"id": 2, "name": "test2"},
            ]
        finally:
            await psql.execute("drop table name")


class TestPsqlCall:
    async def test_call(self, psql):
        table_name = "psqlcall"
        try:
            async with psql() as conn:
                await conn.execute(f"create table {table_name} (id int primary key)")

                await conn.execute(f"insert into {table_name} (id) values (1), (2)")

            check_query = await psql.fetch(f"select * from {table_name}")
            assert len(check_query) == 2

        finally:
            await psql.execute(f"drop table {table_name}")

    async def test_call_error(self, psql):
        """
        Case: There is a syntax error for the second execute statement of the
            transaction and the first one shouldn't be inserted to db.
        """
        table_name = "psqlcallerror"
        try:
            await psql.execute(f"create table {table_name} (id int primary key)")

            try:
                async with psql() as conn:
                    await conn.execute(f"insert into {table_name} (id) values (1), (2)")
                    await conn.execute(f"insert into {table_name} (id) values (3), (4")
            except Exception:
                pass

            check_query = await psql.fetch(f"select * from {table_name}")
            assert not check_query

        finally:
            await psql.execute(f"drop table {table_name}")


class TestPsqlHelpers:
    async def test_get_connection(self, psql):
        """
        Case: Check whether the program can connect to db or not.
        """
        await psql._get_connection()

    def test_get_connection_params(self, psql):
        result = psql._get_connection_params()

        assert result["host"] == "localhost"
        assert result["port"] == 5432
        assert result["user"] == "admin"
        assert result["password"] == "password"
        assert result["database"] == "postgres"
