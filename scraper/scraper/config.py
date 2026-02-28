from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class ScraperSettings(BaseSettings):
    model_config = {
        "env_file": "../../.env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "env_prefix": "SCRAPER_",
    }

    forum_base_url: str = Field(
        default="https://forum.overclockers.ua/viewforum.php?f=26",
        description="Overclockers.ua forum URL",
    )
    forum_base_domain: str = Field(
        default="https://forum.overclockers.ua",
        description="Overclockers.ua forum URL",
    )
    embedding_model: str = Field(
        default="intfloat/multilingual-e5-large",
        description="Embedding model name or local path",
    )
    model_cache_dir: Path = Field(
        default=Path("/app/models"),
        description="Local directory for caching embedding model",
    )
    default_bulk_size: int = Field(
        default=10,
        description="Default number of concurrent requests",
    )
    default_bulk_delay_ms: int = Field(
        default=2000,
        description="Default delay between bulk requests in milliseconds",
    )
    default_page_count: int = Field(
        default=1,
        description="Default number of pages to scrape per run",
    )
    default_user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        description="Default User-Agent header",
    )
    topics_per_page: int = Field(
        default=40,
        description="Number of topics per forum page",
    )
    stale_topic_days: int = Field(
        default=10,
        description="Number of days after which a topic is considered stale for cleanup",
        alias="SEARCH_STALE_TOPIC_DAYS",
    )
    webhook_url: str = Field(
        default="",
        description="Webhook URL to call when scraping completes",
    )


scraper_settings = ScraperSettings()
