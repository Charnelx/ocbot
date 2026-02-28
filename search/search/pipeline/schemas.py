from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ItemCategory(str, Enum):  # noqa: UP042
    CPU = "cpu"
    GPU = "gpu"
    RAM = "ram"
    MOTHERBOARD = "motherboard"
    SSD = "ssd"
    HDD = "hdd"
    PSU = "psu"
    MONITOR = "monitor"
    LAPTOP = "laptop"
    CASE = "case"
    SOUNDCARD = "soundcard"
    OTHER = "other"


class SearchModeUsed(str, Enum):  # noqa: UP042
    SIMPLE = "simple"
    SMART = "smart"
    SMART_FALLBACK = "smart_fallback"


class AgentClassification(BaseModel):
    category: ItemCategory
    labels: list[str] = Field(
        min_length=1,
        description=(
            "Lowercase hyphen-separated technical labels. Same style as enrichment."
        ),
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Self-reported confidence 0.0-1.0 that this classification is correct."
        ),
    )
    reasoning: str = Field(
        description=(
            "One sentence explaining the classification decision. "
            "Used for logging only."
        )
    )


class SearchResultItem(BaseModel):
    item_id: int
    topic_id: int
    topic_url: str
    title: str
    category: str
    labels: list[str]
    price: float | None
    currency: str | None
    is_standalone: bool
    raw_text_segment: str
    author: str
    last_update_at: datetime
    created_at: datetime | None
    score: float


class SearchResponse(BaseModel):
    total_matches: int
    total_filtered: int
    search_mode_used: SearchModeUsed
    results: list[SearchResultItem]
    search_time_seconds: float | None = None
    identified_category: str | None = None
    identified_labels: list[str] | None = None
    auto_tuned_threshold: float | None = None
