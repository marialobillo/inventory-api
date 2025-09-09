from __future__ import annotations
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context
from app.models import Base

# --- App imports (ensure repo root in PYTHONPATH or installed in editable mode)
from app.settings import settings

# When we add models, import metadata like:
# from app.models import Base
target_metadata = Base.metadata

# Alembic Config object
config = context.config

# Use app settings DATABASE_URL (overrides alembic.ini url if present)
if settings.DATABASE_URL:
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
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
        from sqlalchemy.ext.asyncio import create_async_engine
        connectable = create_async_engine(
            config.get_main_option("sqlalchemy.url"),
            poolclass=pool.NullPool,
            future=True,
        )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_async_migrations() -> None:
    asyncio.run(run_migrations_online())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_async_migrations()
