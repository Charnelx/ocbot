from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../../.env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="SEARCH_",
    )

    database_url: str = Field(
        default="postgresql+asyncpg://user:pass@localhost:5432/ocbot",
        alias="DATABASE_URL",
    )
    openrouter_api_key: str = Field(default="")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1")
    llm_model: str = Field(default="arcee-ai/trinity-large-preview:free")
    llm_max_tokens: int = Field(default=1024)
    smart_timeout_seconds: float = Field(default=12.0)
    confidence_threshold: float = Field(default=0.7)
    score_weight_labels: float = Field(default=0.7)
    score_weight_cosine: float = Field(default=0.3)
    min_similarity: float = Field(default=0.2)
    default_limit: int = Field(default=21)
    max_limit: int = Field(default=100)
    max_query_chars: int = Field(default=500)
    wikipedia_timeout_seconds: float = Field(default=5.0)
    wikipedia_max_chars: int = Field(default=1500)
    embedding_model_name: str = Field(default="intfloat/multilingual-e5-large")
    topic_url_template: str = Field(default="{external_id}")
    ranking_algorithm: Literal["recall", "precision"] = Field(default="recall")
    score_auto_tune_step: float = Field(default=0.05)

    @model_validator(mode="after")
    def validate_weights(self) -> "Settings":
        total = self.score_weight_labels + self.score_weight_cosine
        if not (0.99 <= total <= 1.01):
            raise ValueError(
                f"score_weight_labels ({self.score_weight_labels}) + "
                f"score_weight_cosine ({self.score_weight_cosine}) must equal 1.0"
            )
        return self


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
