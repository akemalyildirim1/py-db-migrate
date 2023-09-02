"""Common test objects."""
import pytest
from shutil import rmtree
from uuid import uuid4
import os


@pytest.fixture
def use_temp_file():
    file_name = f"./temp-{uuid4()}"
    os.mkdir(file_name)
    yield file_name
    rmtree(file_name)
