from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
  """Declarative base for ORM models."""


_engine: AsyncEngine | None = None
_SessionLocal: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
  global _engine
  if _engine is None:
    _engine = create_async_engine(
      settings.async_database_url,
      echo=False,
      pool_pre_ping=True,
    )
  return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
  global _SessionLocal
  if _SessionLocal is None:
    _SessionLocal = async_sessionmaker(bind=get_engine(), expire_on_commit=False)
  return _SessionLocal


@asynccontextmanager
async def lifespan_session() -> AsyncIterator[AsyncSession]:
  """Provide an async session for background tasks."""
  async_session = get_session_factory()
  async with async_session() as session:
    yield session


async def verify_database_connection() -> None:
  async with get_engine().begin() as connection:
    await connection.run_sync(lambda _: None)


async def dispose_engine() -> None:
  engine = get_engine()
  await engine.dispose()
