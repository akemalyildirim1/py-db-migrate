"""Test database init file."""

from py_db_migrate.database import Sql


class SqlConcrete(Sql):
    async def execute(self, query):
        raise NotImplementedError

    async def fetch(self, query):
        raise NotImplementedError


class TestSql:
    def test_sql(self):
        """
        Case: Try to instantiate a sql class.
        """
        sql_concrete_class = SqlConcrete(
            database="postgres",
            user="admin",
            password="password",
            host="database.service.com",
            port="5432",
        )

        assert sql_concrete_class.database == "postgres"
        assert sql_concrete_class.user == "admin"
        assert sql_concrete_class.password == "password"
        assert sql_concrete_class.port == "5432"
        assert sql_concrete_class.host == "database.service.com"
