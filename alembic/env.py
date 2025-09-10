# alembic/env.py
from __future__ import annotations
import asyncio
from logging.config import fileConfig
from typing import Optional, cast

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.settings import settings
from app.models import Base

# ---- Alembic config ----
config = context.config

# Prioriza DATABASE_URL de settings .env
db_url: Optional[str] = settings.DATABASE_URL
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# Logging de Alembic
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata objetivo para autogenerate
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise RuntimeError("DATABASE_URL (sqlalchemy.url) is not configured.")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = context.config.attributes.get("connection", None)

    if connectable is None:
        url = config.get_main_option("sqlalchemy.url")
        if not url:
            raise RuntimeError("DATABASE_URL (sqlalchemy.url) is not configured.")
        # anota tipo para Pylance
        connectable = cast(
            AsyncEngine,
            create_async_engine(url, poolclass=pool.NullPool),
        )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()  # type: ignore[attr-defined]

def run_async_migrations() -> None:
    asyncio.run(run_migrations_online())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_async_migrations()
