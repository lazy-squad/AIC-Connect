from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from aic_hub import db
from aic_hub.config import settings
from aic_hub.main import app


@pytest.fixture(autouse=True)
async def _setup_database(tmp_path) -> AsyncIterator[None]:
  database_path = tmp_path / "test.db"
  settings.database_url = f"sqlite+aiosqlite:///{database_path.as_posix()}"
  settings.session_cookie.secure = False

  db._engine = None  # type: ignore[attr-defined]
  db._SessionLocal = None  # type: ignore[attr-defined]
  engine = db.get_engine()

  async with engine.begin() as connection:
    await connection.run_sync(db.Base.metadata.create_all)

  yield

  async with engine.begin() as connection:
    await connection.run_sync(db.Base.metadata.drop_all)

  await engine.dispose()
  db._engine = None  # type: ignore[attr-defined]
  db._SessionLocal = None  # type: ignore[attr-defined]


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
  transport = ASGITransport(app=app)
  async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
    yield http_client


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
  session_factory = db.get_session_factory()
  async with session_factory() as async_session:
    yield async_session
