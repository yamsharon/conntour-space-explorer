"""Controller for handling search-related API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_search_service
from app.domain.models import SearchResult
from app.domain.services.search_service import SearchService
from app.utils.constants import NORMALIZED_MINIMUM, NORMALIZED_MAXIMUM
from app.utils.logger import logger


class SearchController:
    """Controller for managing search endpoints."""

    def __init__(self):
        """Initialize the SearchController."""
        logger.info("Initializing SearchController")
        self.router = APIRouter(prefix="/api", tags=["search"])
        self.router.get("/search", response_model=List[SearchResult])(self.search_sources)

    @staticmethod
    def search_sources(
            q: str = Query("", description="Natural language search query"),
            limit: int = Query(15, description="Maximum number of results", ge=1, le=100),
            skipHistory: bool = Query(False,
                                      description="Skip saving to history (e.g., when navigating from history page)"),
            search_service: SearchService = Depends(get_search_service)
    ) -> List[SearchResult]:
        f"""
        Search for NASA images using natural language queries.
        Return results with confidence scores between {NORMALIZED_MINIMUM} and {NORMALIZED_MAXIMUM}.

        Args:
            q: Natural language search query (e.g., "images of Mars rovers", "solar flares")
            limit: Maximum number of results to return (1-100)
            skipHistory: If True, don't save this search to history
            search_service: Injected search service

        Returns:
            List of SearchResult objects with confidence scores {NORMALIZED_MINIMUM} and {NORMALIZED_MAXIMUM}
        """
        # Handle empty query - return empty list early
        if not q or not q.strip():
            logger.info("Empty search query provided, returning empty results")
            return []

        logger.info(f"Searching for: '{q}' with limit of {limit} results (skipHistory={skipHistory})")
        results = search_service.search(query=q, limit=limit, save_to_history=not skipHistory)
        logger.info(f"Found {len(results)} results")
        return results
