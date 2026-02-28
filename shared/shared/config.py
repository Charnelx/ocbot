from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ocbot",
        alias="DATABASE_URL",
        description="PostgreSQL connection URL (postgresql+asyncpg://user:pass@host:port/db)",
    )
    log_level: str = Field(
        default="INFO", alias="LOG_LEVEL", description="Logging level"
    )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
