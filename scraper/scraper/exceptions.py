class ScraperError(Exception):
    """Base exception for scraper service."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause


class ForumFetchError(ScraperError):
    """Failed to fetch from forum."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message, cause)


class TopicParseError(ScraperError):
    """Failed to parse topic HTML."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message, cause)


class ContentCleanError(ScraperError):
    """Failed to clean content."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message, cause)


class EmbeddingError(ScraperError):
    """Failed to generate embeddings."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message, cause)


class DatabaseError(ScraperError):
    """Failed to save to database."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message, cause)
