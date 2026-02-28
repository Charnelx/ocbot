from dataclasses import dataclass

from sqlalchemy import text

from search.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RecomputeStatsResult:
    success: bool
    total_items: int
    avg_label_count: float
    unique_labels: int
    max_idf: float
    message: str


async def recompute_stats() -> RecomputeStatsResult:
    from shared.db import async_session_factory

    async with async_session_factory() as session:
        total_items_result = await session.execute(
            text("SELECT COUNT(*) FROM items WHERE labels IS NOT NULL")
        )
        total_items: int = total_items_result.scalar() or 0

        if total_items == 0:
            return RecomputeStatsResult(
                success=True,
                total_items=0,
                avg_label_count=0.0,
                unique_labels=0,
                max_idf=1.0,
                message="No items found, stats set to zero",
            )

        avg_result = await session.execute(
            text(
                "SELECT AVG(array_length(labels, 1)) FROM items "
                "WHERE labels IS NOT NULL AND array_length(labels, 1) > 0"
            )
        )
        avg_label_count: float = float(avg_result.scalar() or 0.0)

        await session.execute(
            text("TRUNCATE TABLE label_stats RESTART IDENTITY CASCADE")
        )

        await session.execute(
            text("""
            INSERT INTO label_stats (label, df)
            SELECT label, COUNT(*) as df
            FROM items,
                 unnest(CASE WHEN labels IS NOT NULL THEN labels ELSE '{}' END) as label
            GROUP BY label
        """)
        )

        unique_labels_result = await session.execute(
            text("SELECT COUNT(*) FROM label_stats")
        )
        unique_labels: int = unique_labels_result.scalar() or 0

        max_idf_result = await session.execute(
            text("SELECT MAX(LN(1 + :total_items / df)) FROM label_stats WHERE df > 0"),
            {"total_items": total_items},
        )
        raw_max_idf = max_idf_result.scalar() or 1.0
        max_idf: float = float(raw_max_idf) if raw_max_idf > 0 else 1.0

        await session.execute(
            text("""
                UPDATE search_stats
                SET total_items = :total_items,
                    avg_label_count = :avg_label_count,
                    max_idf = :max_idf,
                    updated_at = NOW()
                WHERE id = 1
            """),
            {
                "total_items": total_items,
                "avg_label_count": avg_label_count,
                "max_idf": max_idf,
            },
        )

        await session.commit()

        logger.info(
            "stats_recomputed",
            total_items=total_items,
            avg_label_count=avg_label_count,
            unique_labels=unique_labels,
            max_idf=max_idf,
        )

        return RecomputeStatsResult(
            success=True,
            total_items=total_items,
            avg_label_count=avg_label_count,
            unique_labels=unique_labels,
            max_idf=max_idf,
            message=(
                f"Successfully recomputed stats: {total_items} items, "
                f"{unique_labels} unique labels"
            ),
        )
