from pydantic import Field
from pydantic.types import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../../.env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="ENRICHMENT_",
    )

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ocbot",
        description="PostgreSQL connection URL",
    )
    openrouter_api_key: SecretStr = Field(
        default=SecretStr(""),
        description="OpenRouter API key for LLM calls",
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter base URL",
    )
    llm_model: str = Field(
        default="arcee-ai/trinity-large-preview:free",
        description="LLM model for extraction",
    )
    llm_max_attempts: int = Field(
        default=3,
        description="Total LLM attempts including initial",
    )
    llm_retry_min_wait: float = Field(
        default=2.0,
        description="Tenacity backoff floor in seconds",
    )
    llm_retry_max_wait: float = Field(
        default=5.0,
        description="Tenacity backoff ceiling in seconds",
    )
    llm_max_tokens: int = Field(
        default=8096,
        description="Max tokens for LLM output",
    )
    enrich_default_limit: int = Field(
        default=10,
        description="Topics per run when limit omitted",
    )
    enrich_max_limit: int = Field(
        default=100,
        description="Hard cap on any single run",
    )
    enrichment_concurrency: int = Field(
        default=5,
        description="Number of concurrent requests to model provider",
    )
    max_topic_attempts: int = Field(
        default=3,
        description="Permanent exclusion threshold",
    )
    max_content_chars: int = Field(
        default=6000,
        description="Content truncation limit",
    )
    embedding_model: str = Field(
        default="intfloat/multilingual-e5-large",
        description="Embedding model name",
    )
    webhook_url: str = Field(
        default="",
        description="Webhook URL to call when enrichment completes",
    )


settings = Settings()


def get_settings() -> Settings:
    return settings
