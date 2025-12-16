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
        self.search_service = search_service
        self.router = APIRouter(prefix="/api", tags=["search"])
        self._register_routes()

    def _register_routes(self):
        """Register all routes for this controller."""
        self.router.get("/search", response_model=List[SearchResult])(self.search_sources)

    def search_sources(
        self,
        q: str = Query(..., description="Natural language search query", min_length=1),
        limit: int = Query(10, description="Maximum number of results", ge=1, le=100),
    ) -> List[SearchResult]:
        """
        Search for NASA images using natural language queries.

        Uses semantic search with CLIP embeddings to find images that match the query.
        Return results with confidence scores based on semantic similarity.

        Args:
            q: Natural language search query (e.g., "images of Mars rovers", "solar flares")
            limit: Maximum number of results to return (1-100)

        Returns:
            List of SearchResult objects with confidence scores in range [0, 1]
        """
        logger.info(f"Search request: query='{q}', limit={limit}")
        results = self.search_service.search(query=q, limit=limit)
        logger.info(f"Search returned {len(results)} results")
        return results
