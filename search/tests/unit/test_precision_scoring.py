import pytest
from math import log

from search.pipeline.smart import _apply_precision_scoring


class TestPrecisionScoring:
    def test_score_bounds_zero_to_one(self):
        label_df = {"rtx-4080": 10, "gpu": 100, "nvidia": 50}
        total_items = 1000
        avg_label_count = 3.0
        max_idf = log(1 + 1000 / 10)

        score = _apply_precision_scoring(
            agent_labels=["rtx-4080", "gpu"],
            item_labels=["rtx-4080", "gpu", "nvidia"],
            cosine_sim=0.8,
            label_df=label_df,
            total_items=total_items,
            avg_label_count=avg_label_count,
            max_idf=max_idf,
        )
        assert 0.0 <= score <= 1.0

    def test_more_matches_higher_score(self):
        label_df = {"rtx-4080": 10, "gpu": 100, "nvidia": 50, "16gb": 200}
        total_items = 1000
        avg_label_count = 3.0
        max_idf = log(1 + 1000 / 10)

        score_partial = _apply_precision_scoring(
            agent_labels=["rtx-4080", "gpu", "nvidia"],
            item_labels=["rtx-4080"],
            cosine_sim=0.5,
            label_df=label_df,
            total_items=total_items,
            avg_label_count=avg_label_count,
            max_idf=max_idf,
        )

        score_full = _apply_precision_scoring(
            agent_labels=["rtx-4080", "gpu", "nvidia"],
            item_labels=["rtx-4080", "gpu", "nvidia"],
            cosine_sim=0.5,
            label_df=label_df,
            total_items=total_items,
            avg_label_count=avg_label_count,
            max_idf=max_idf,
        )

        assert score_full > score_partial

    def test_higher_specificity_more_label_weight(self):
        label_df = {"rtx-4080": 10, "rare-chip": 5, "gpu": 100}
        total_items = 1000
        avg_label_count = 3.0
        max_idf = log(1 + 1000 / 5)

        score_generic = _apply_precision_scoring(
            agent_labels=["gpu"],
            item_labels=["gpu", "nvidia"],
            cosine_sim=0.3,
            label_df=label_df,
            total_items=total_items,
            avg_label_count=avg_label_count,
            max_idf=max_idf,
        )

        score_specific = _apply_precision_scoring(
            agent_labels=["rtx-4080", "rare-chip"],
            item_labels=["rtx-4080", "rare-chip", "gpu"],
            cosine_sim=0.3,
            label_df=label_df,
            total_items=total_items,
            avg_label_count=avg_label_count,
            max_idf=max_idf,
        )

        assert score_specific > score_generic

    def test_longer_label_list_mild_penalty(self):
        label_df = {"rtx-4080": 10, "gpu": 100}
        total_items = 1000
        avg_label_count = 3.0
        max_idf = log(1 + 1000 / 10)

        score_short = _apply_precision_scoring(
            agent_labels=["rtx-4080", "gpu"],
            item_labels=["rtx-4080", "gpu"],
            cosine_sim=0.5,
            label_df=label_df,
            total_items=total_items,
            avg_label_count=avg_label_count,
            max_idf=max_idf,
        )

        score_long = _apply_precision_scoring(
            agent_labels=["rtx-4080", "gpu"],
            item_labels=["rtx-4080", "gpu", "nvidia", "16gb", "ddr6", " Ada"],
            cosine_sim=0.5,
            label_df=label_df,
            total_items=total_items,
            avg_label_count=avg_label_count,
            max_idf=max_idf,
        )

        assert score_short > score_long
        penalty_ratio = (score_short - score_long) / score_short
        assert penalty_ratio < 0.3

    def test_empty_agent_labels_returns_cosine(self):
        score = _apply_precision_scoring(
            agent_labels=[],
            item_labels=["rtx-4080", "gpu"],
            cosine_sim=0.7,
            label_df={},
            total_items=1000,
            avg_label_count=3.0,
            max_idf=2.0,
        )
        assert score == 0.7

    def test_zero_overlap_returns_low_score(self):
        label_df = {"rtx-4080": 10, "gpu": 100}
        total_items = 1000
        avg_label_count = 3.0
        max_idf = log(1 + 1000 / 10)

        score = _apply_precision_scoring(
            agent_labels=["rtx-4080", "gpu"],
            item_labels=["amd", "radeon", "rx-7800xt"],
            cosine_sim=0.9,
            label_df=label_df,
            total_items=total_items,
            avg_label_count=avg_label_count,
            max_idf=max_idf,
        )
        assert 0.0 <= score <= 1.0
        assert score < 0.5

    def test_missing_label_in_stats_uses_max_idf(self):
        label_df = {"rtx-4080": 10}
        total_items = 1000
        avg_label_count = 3.0
        max_idf = log(1 + 1000 / 10)

        score = _apply_precision_scoring(
            agent_labels=["rtx-4080", "unknown-label"],
            item_labels=["rtx-4080"],
            cosine_sim=0.5,
            label_df=label_df,
            total_items=total_items,
            avg_label_count=avg_label_count,
            max_idf=max_idf,
        )
        assert 0.0 <= score <= 1.0
        assert score > 0.0
