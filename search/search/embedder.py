from sentence_transformers import SentenceTransformer

from search.config import settings
from search.logging import get_logger

logger = get_logger(__name__)

_embedder: SentenceTransformer | None = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        logger.debug("Loading embedding model", model=settings.embedding_model_name)
        _embedder = SentenceTransformer(settings.embedding_model_name)
    return _embedder


def embed_query(query: str) -> list[float]:
    prefixed = f"query: {query}"
    return _get_embedder().encode([prefixed])[0].tolist()
