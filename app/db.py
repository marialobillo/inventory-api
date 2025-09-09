from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .settings import settings

engine = create_async_engine(
  settings.DATABASE_URL,
  echo=settings.SQL_ECHO,
  future=True
)

SessionLocal = async_sessionmaker(
  bind=engine,
  expire_on_commit=False,
  class_=AsyncSession,
)

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
