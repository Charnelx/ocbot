import numpy as np
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_sentence_transformer():
    with patch("scraper.ingestion.embedder.SentenceTransformer") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        yield mock_cls, mock_instance


@pytest.fixture
def embedder():
    from scraper.ingestion.embedder import TopicEmbedder
    return TopicEmbedder(model_name="test-model")


class TestTopicEmbedder:

    def test_model_not_loaded_on_init(self, embedder):
        assert embedder.model is None

    def test_load_model_initializes_sentence_transformer(self, embedder, mock_sentence_transformer):
        mock_cls, _ = mock_sentence_transformer

        embedder.load_model()

        mock_cls.assert_called_once_with("test-model")
        assert embedder.model is not None

    def test_embed_lazy_loads_model(self, embedder, mock_sentence_transformer):
        mock_cls, mock_instance = mock_sentence_transformer
        mock_instance.encode.return_value = np.array([[0.1, 0.2, 0.3]])

        embedder.embed(["some text"])

        mock_cls.assert_called_once()  # model was loaded on first call

    def test_embed_does_not_reload_model_on_second_call(self, embedder, mock_sentence_transformer):
        mock_cls, mock_instance = mock_sentence_transformer
        mock_instance.encode.return_value = np.array([[0.1, 0.2, 0.3]])

        embedder.embed(["first"])
        embedder.embed(["second"])

        mock_cls.assert_called_once()  # still only one instantiation

    def test_embed_returns_list_of_float_lists(self, embedder, mock_sentence_transformer):
        _, mock_instance = mock_sentence_transformer
        mock_instance.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])

        result = embedder.embed(["text one", "text two"])

        assert result == [[0.1, 0.2], [0.3, 0.4]]
        assert isinstance(result[0], list)
        assert isinstance(result[0][0], float)

    def test_embed_calls_encode_with_correct_args(self, embedder, mock_sentence_transformer):
        _, mock_instance = mock_sentence_transformer
        mock_instance.encode.return_value = np.array([[0.1, 0.2]])

        embedder.embed(["hello world"])

        mock_instance.encode.assert_called_once_with(
            ["hello world"],
            convert_to_numpy=True,
            show_progress_bar=False,
        )

    def test_embed_single_returns_single_embedding(self, embedder, mock_sentence_transformer):
        _, mock_instance = mock_sentence_transformer
        mock_instance.encode.return_value = np.array([[0.5, 0.6, 0.7]])

        result = embedder.embed_single("hello")

        assert result == [0.5, 0.6, 0.7]
        assert isinstance(result, list)

    def test_embed_single_wraps_text_in_list_for_encode(self, embedder, mock_sentence_transformer):
        _, mock_instance = mock_sentence_transformer
        mock_instance.encode.return_value = np.array([[0.1, 0.2]])

        embedder.embed_single("solo text")

        mock_instance.encode.assert_called_once_with(
            ["solo text"],  # confirm the wrapping happens correctly
            convert_to_numpy=True,
            show_progress_bar=False,
        )
