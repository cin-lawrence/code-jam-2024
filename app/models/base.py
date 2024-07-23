from collections.abc import Callable
from typing import Any, Sequence

from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase


class classproperty:
    """
    Decorator that converts a method with a single cls argument into a property
    that can be accessed directly from the class.
    """

    def __init__(self, method: Callable[..., Any]) -> None:
        self.fget = method

    def __get__(self, instance: Any, cls: type) -> Any:
        return self.fget(cls)

    def getter(self, method: Callable[..., Any]) -> "classproperty":
        self.fget = method
        return self


class Base(DeclarativeBase):
    @classproperty
    def relationships(cls) -> Sequence[str]:
        """Return all relationship columns."""
        return cls.__mapper__.relationships.keys()

    @classproperty
    def columns(cls) -> Sequence[str]:
        return [column.key for column in inspect(cls).mapper.attrs]
