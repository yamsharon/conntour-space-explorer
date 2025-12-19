"""Dependency injection for FastAPI routes."""

from functools import lru_cache

from app.domain.services.history_service import HistoryService
from app.domain.services.search_service import SearchService
from app.domain.services.sources_service import SourcesService
from app.infra.db import SpaceDB
from app.infra.language_model import LanguageModel
from app.utils.logger import logger


# Infrastructure dependencies (singletons)
@lru_cache()
def get_language_model() -> LanguageModel:
    """Get the language model instance (singleton)."""
    logger.debug("Getting language model instance")
    return LanguageModel()


@lru_cache()
def get_db() -> SpaceDB:
    """Get the database instance (singleton)."""
    logger.debug("Getting database instance")
    lm = get_language_model()
    return SpaceDB(lm)


# Service dependencies (cached to ensure singleton behavior)
@lru_cache()
def get_sources_service() -> SourcesService:
    """Get the sources service instance (singleton)."""
    logger.debug("Getting sources service instance")
    db = get_db()
    return SourcesService(db=db)


@lru_cache()
def get_history_service() -> HistoryService:
    """Get the history service instance (singleton)."""
    logger.debug("Getting history service instance")
    db = get_db()
    return HistoryService(db=db)


@lru_cache()
def get_search_service() -> SearchService:
    """Get the search service instance (singleton)."""
    logger.debug("Getting search service instance")
    db = get_db()
    lm = get_language_model()
    history_service = get_history_service()
    return SearchService(db=db, lm=lm, history_service=history_service)

