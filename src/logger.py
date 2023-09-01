"""Logger functions for all modules."""
import logging
import os
from functools import lru_cache

logging.basicConfig(
    level=logging.DEBUG,
    format=("(%(levelname)s) %(message)s"),
    handlers=[logging.StreamHandler()],
)


@lru_cache(maxsize=1)
def get_logger() -> logging.Logger:
    """Return logger object."""
    return logging.getLogger()


get_logger().setLevel(os.environ.get("LOG_LEVEL", "info").upper())
