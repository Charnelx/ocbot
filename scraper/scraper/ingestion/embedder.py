import logging
import time
from pathlib import Path

from sentence_transformers import SentenceTransformer

from scraper.config import scraper_settings

logger = logging.getLogger(__name__)


class TopicEmbedder:
    def __init__(self, model_name: str | None = None, model_path: Path | None = None):
        self.model_name = model_name or scraper_settings.embedding_model
        self.model_path = model_path or scraper_settings.model_cache_dir
        self.model: SentenceTransformer | None = None

    def load_model(self) -> None:
        start_time = time.time()

        model_dir = self.model_path / self.model_name.replace("/", "_")
        if model_dir.exists() and (model_dir / "config.json").exists():
            logger.info("Loading embedding model from local cache", extra={"model_dir": str(model_dir)})
            self.model = SentenceTransformer(str(model_dir))
        else:
            logger.info("Downloading embedding model", extra={"model_name": self.model_name})
            self.model = SentenceTransformer(self.model_name)
            self.model.save(str(model_dir))
            logger.info("Embedding model saved to cache", extra={"model_dir": str(model_dir)})

        load_time = time.time() - start_time
        logger.info("Embedding model loaded", extra={"load_time_sec": load_time})

    def embed(self, texts: list[str]) -> list[list[float]]:
        if self.model is None:
            self.load_model()

        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

        result: list[list[float]] = [embedding.tolist() for embedding in embeddings]
        logger.debug("Generated embeddings", extra={"count": len(result)})
        return result

    def embed_single(self, text: str) -> list[float]:
        return self.embed([text])[0]
