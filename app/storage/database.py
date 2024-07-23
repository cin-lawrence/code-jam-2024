import json
import logging
import socket
from asyncio import current_task
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import cached_property
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)


class Database:
    def __init__(self, url: str, **kw: Any) -> None:
        self.engine = create_async_engine(
            url,
            pool_pre_ping=True,
            echo=kw.pop('echo', False),
        )

    @cached_property
    def AsyncSessionMaker(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def create_session(self) -> AsyncIterator[AsyncSession]:
        async with self.AsyncSessionMaker() as async_session:
            try:
                yield async_session
            except Exception:
                await async_session.rollback()
                raise
            finally:
                await async_session.close()


# TODO: move this to a container
database = Database('sqlite+aiosqlite:///./test.db', echo=True)
