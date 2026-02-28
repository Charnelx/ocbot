from enum import StrEnum

from pydantic import BaseModel, Field


class ItemCategory(StrEnum):
    cpu = "cpu"
    gpu = "gpu"
    ram = "ram"
    motherboard = "motherboard"
    ssd = "ssd"
    hdd = "hdd"
    psu = "psu"
    monitor = "monitor"
    laptop = "laptop"
    case = "case"
    soundcard = "soundcard"
    other = "other"


class ItemCurrency(StrEnum):
    UAH = "UAH"
    USD = "USD"
    EUR = "EUR"


class ExtractedItem(BaseModel):
    title: str = Field(
        description=(
            "Clean product title. No price, condition, or seller notes. "
            "E.g. 'Intel Core i7-12700K', 'ASUS ROG STRIX RTX 3080 10GB'."
        )
    )
    raw_text_segment: str = Field(
        description=(
            "The verbatim text fragment from the post that describes this specific item, including any price. Used for audit."
        )
    )
    category: ItemCategory = Field(
        description=(
            "Product category. Use 'other' only if no specific category fits. "
            "Peripherals (mouse, keyboard, headset) and complete pre-built systems → 'other'."
        )
    )
    labels: list[str] = Field(
        min_length=1,
        description=(
            "Lowercase hyphen-separated technical attributes you know with HIGH CONFIDENCE. "
            "Include: brand, product line, generation codename, platform/socket, form factor, "
            "capacity, speed tier. Omit any attribute you are uncertain about."
        ),
    )
    price: float | None = Field(
        ge=0,
        description="Numeric price only. Null if no price is stated anywhere in the segment.",
    )
    currency: ItemCurrency | None = Field(
        description=(
            "Currency of the stated price. Null if price is null. "
            "Map: грн/₴/гривень/UAH → UAH. $/usd/долар → USD. €/eur/євро → EUR."
        ),
    )


class ExtractionResult(BaseModel):
    items: list[ExtractedItem] = Field(
        description=("All distinct items offered for sale. One record per distinct product. Empty list if nothing is for sale.")
    )
