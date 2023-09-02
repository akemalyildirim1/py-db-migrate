"""Service module."""
from abc import ABC
from pydantic import BaseModel, ConfigDict


class ServiceABC(ABC, BaseModel):
    """ServiceABC class."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
