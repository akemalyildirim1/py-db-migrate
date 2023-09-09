"""Common test objects."""
import pytest
from shutil import rmtree
from uuid import uuid4
import os

from py_db_migrate.database.postgresql import PSql


@pytest.fixture
def psql() -> PSql:
    return PSql(
        user="admin",
        password="password",
        host="localhost",
        port=5432,
        name="postgres",
    )


@pytest.fixture
def use_temp_file():
    file_name = f"./temp-{uuid4()}"
    os.mkdir(file_name)
    yield file_name
    rmtree(file_name)
