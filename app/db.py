# app/db.py
from typing import AsyncGenerator  # 👈 importa el tipo correcto
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
)

# opcional: ayuda a Pylance/Mypy con el tipo del factory
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# 👇 es un async generator dependency para FastAPI
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            # el context manager ya cierra, pero lo dejamos explícito
            await session.close()
