import hashlib
import logging

logger = logging.getLogger(__name__)


def compute_hash(content: str) -> str:
    hash_value = hashlib.sha256(content.encode("utf-8")).hexdigest()
    logger.debug(
        "Content hashed",
        extra={"content_length": len(content), "hash": hash_value[:16]},
    )
    return hash_value
