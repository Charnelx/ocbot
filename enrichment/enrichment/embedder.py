from sentence_transformers import SentenceTransformer

from enrichment.config import get_settings

settings = get_settings()

_embedder: SentenceTransformer | None = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(settings.embedding_model)
    return _embedder


def get_embedder() -> SentenceTransformer:
    return _get_embedder()


def embed_text(text: str) -> list[float]:
    return _get_embedder().encode([text])[0].tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    return _get_embedder().encode(texts).tolist()
