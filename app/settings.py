from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  ENV: str = "dev"
  DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"
  SQL_ECHO: bool = False

  class Config:
    env_file = ".env"
    extra = "ignore"

settings = Settings()