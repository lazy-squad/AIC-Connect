from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from aic_hub.config import settings
from aic_hub.db import Base
# Import all models to ensure they are registered with SQLAlchemy
from aic_hub import models  # noqa: F401

config = context.config

if config.config_file_name:
  fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.async_database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
  context.configure(
    url=settings.async_database_url,
    target_metadata=target_metadata,
    literal_binds=True,
    dialect_opts={"paramstyle": "named"},
  )

  with context.begin_transaction():
    context.run_migrations()


async def run_migrations_online() -> None:
  connectable = async_engine_from_config(
    config.get_section(config.config_ini_section, {}),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
    future=True,
  )

  async with connectable.connect() as connection:
    await connection.run_sync(do_run_migrations)

  await connectable.dispose()


def do_run_migrations(connection: Connection) -> None:
  context.configure(connection=connection, target_metadata=target_metadata)

  with context.begin_transaction():
    context.run_migrations()


def run_migrations() -> None:
  if context.is_offline_mode():
    run_migrations_offline()
  else:
    asyncio.run(run_migrations_online())


if __name__ == "__main__":
  run_migrations()
