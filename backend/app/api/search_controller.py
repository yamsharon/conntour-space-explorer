"""Controller for handling search-related API endpoints."""

from typing import List

from fastapi import APIRouter, Query

from app.domain.models import SearchResult
from app.domain.services.search_service import SearchService
from app.utils.logger import logger


class SearchController:
    """Controller for managing search endpoints."""

    def __init__(self, search_service: SearchService):
        """
        Initialize the SearchController.

        Args:
            search_service: Service for performing semantic search over NASA images
        """
        logger.info("Initializing SearchController")
        self.search_service = search_service
        self.router = APIRouter(prefix="/api", tags=["search"])
        self.router.get("/search", response_model=List[SearchResult])(self.search_sources)

    def search_sources(
        self,
        q: str = Query("", description="Natural language search query"),
        limit: int = Query(15, description="Maximum number of results", ge=1, le=100),
    ) -> List[SearchResult]:
        """
        Search for NASA images using natural language queries.
        Return results with confidence scores between 0.2 and 1.0.

        Args:
            q: Natural language search query (e.g., "images of Mars rovers", "solar flares")
            limit: Maximum number of results to return (1-100)

        Returns:
            List of SearchResult objects with confidence scores between 0.2 and 1.0
        """
        # Handle empty query - return empty list early
        if not q or not q.strip():
            logger.info("Empty search query provided, returning empty results")
            return []

        logger.info(f"Searching for: '{q}' with limit of {limit} results")
        results = self.search_service.search(query=q, limit=limit)
        logger.info(f"Found {len(results)} results")
        return results
