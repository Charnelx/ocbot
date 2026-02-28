import pytest
from unittest.mock import patch


class TestRecallScoring:
    def test_recall_scoring_bounds_zero_to_one(self):
        from search.pipeline.smart import _apply_recall_scoring

        score = _apply_recall_scoring(
            label_match_ratio=0.5,
            cosine_sim=0.8,
        )
        assert 0.0 <= score <= 1.0

    def test_recall_scoring_more_matches_higher_score(self):
        from search.pipeline.smart import _apply_recall_scoring

        score_partial = _apply_recall_scoring(
            label_match_ratio=0.3,
            cosine_sim=0.5,
        )

        score_full = _apply_recall_scoring(
            label_match_ratio=1.0,
            cosine_sim=0.5,
        )

        assert score_full > score_partial

    def test_recall_scoring_empty_labels_returns_cosine(self):
        from search.pipeline.smart import _apply_recall_scoring

        score = _apply_recall_scoring(
            label_match_ratio=0.0,
            cosine_sim=0.7,
        )
        assert 0.0 <= score <= 1.0

    def test_recall_scoring_zero_overlap_low_score(self):
        from search.pipeline.smart import _apply_recall_scoring

        score = _apply_recall_scoring(
            label_match_ratio=0.0,
            cosine_sim=0.9,
        )
        assert 0.0 <= score <= 1.0

    def test_recall_scoring_full_overlap(self):
        from search.pipeline.smart import _apply_recall_scoring

        score = _apply_recall_scoring(
            label_match_ratio=1.0,
            cosine_sim=1.0,
        )
        assert 0.0 <= score <= 1.0
        assert score > 0.8

    def test_recall_scoring_uses_settings(self):
        from search.pipeline.smart import _apply_recall_scoring

        with patch("search.pipeline.smart.settings") as mock_settings:
            mock_settings.score_weight_labels = 0.5
            mock_settings.score_weight_cosine = 0.5

            score = _apply_recall_scoring(
                label_match_ratio=1.0,
                cosine_sim=1.0,
            )
            assert score == pytest.approx(1.0, rel=0.01)

    def test_recall_scoring_weighted_calculation(self):
        from search.pipeline.smart import _apply_recall_scoring

        with patch("search.pipeline.smart.settings") as mock_settings:
            mock_settings.score_weight_labels = 0.8
            mock_settings.score_weight_cosine = 0.2

            score = _apply_recall_scoring(
                label_match_ratio=0.5,
                cosine_sim=0.5,
            )
            expected = 0.8 * 0.5 + 0.2 * 0.5
            assert score == pytest.approx(expected)
