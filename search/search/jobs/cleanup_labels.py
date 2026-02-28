from dataclasses import dataclass

from sqlalchemy import select, func

from search.logging import get_logger
from shared.models import Item

logger = get_logger(__name__)

EXCEPTED_2CHAR_LABELS = {"hp", "wd", "lg", "m2"}
LABEL_REPLACEMENTS = {
    "i3": "core-i3",
    "i5": "core-i5",
    "i7": "core-i7",
    "i9": "core-i9",
}
BATCH_SIZE = 100


@dataclass
class CleanupLabelsResult:
    items_cleaned: int
    items_deleted: int


def _clean_labels(labels: list[str]) -> list[str]:
    cleaned = []
    for label in labels:
        replaced = LABEL_REPLACEMENTS.get(label, label)
        length = len(replaced)

        if length == 1:
            continue
        if length == 2 and replaced.lower() not in EXCEPTED_2CHAR_LABELS:
            continue

        cleaned.append(replaced)

    return cleaned


async def cleanup_labels() -> CleanupLabelsResult:
    from shared.db import async_session_factory

    items_cleaned = 0
    items_deleted = 0
    offset = 0

    while True:
        async with async_session_factory() as session:
            result = await session.execute(
                select(Item).offset(offset).limit(BATCH_SIZE)
            )
            items = result.scalars().all()

            if not items:
                break

            for item in items:
                original_labels = item.labels or []
                cleaned_labels = _clean_labels(original_labels)

                if not cleaned_labels:
                    logger.info(
                        "item_deleted",
                        item_id=item.id,
                        topic_id=item.topic_id,
                        title=item.title,
                        category=item.category,
                        price=str(item.price) if item.price else None,
                    )
                    await session.delete(item)
                    items_deleted += 1
                elif cleaned_labels != original_labels:
                    item.labels = cleaned_labels
                    items_cleaned += 1

            await session.commit()

            if len(items) < BATCH_SIZE:
                break

            offset += BATCH_SIZE

    return CleanupLabelsResult(
        items_cleaned=items_cleaned,
        items_deleted=items_deleted,
    )
