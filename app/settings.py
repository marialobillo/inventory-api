from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    ENV: str = 'dev'
    DATABASE_URL: str = ''    
    SQL_ECHO: bool = False

    def ensure(self) -> 'Settings':
        if not self.DATABASE_URL:
            raise RuntimeError('DATABASE_URL environment variable is required')
        return self

settings = Settings().ensure()