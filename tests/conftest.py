"""Common test objects."""
import pytest
from shutil import rmtree
import os


@pytest.fixture
def use_temp_file():
    os.mkdir("./temp")
    yield
    rmtree("./temp")
