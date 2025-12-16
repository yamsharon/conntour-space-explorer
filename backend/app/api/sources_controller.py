"""Controller for handling sources-related API endpoints."""

from typing import List

from fastapi import APIRouter

from app.domain.models import Source
from app.domain.services.sources_service import SourcesService
from app.utils.logger import logger


class SourcesController:
    """Controller for managing sources endpoints."""

    def __init__(self, sources_service: SourcesService):
        """
        Initialize the SourcesController.

        Args:
            sources_service: Service for fetching NASA image sources
        """
        self.sources_service = sources_service
        self.router = APIRouter(prefix="/api", tags=["sources"])
        self._register_routes()

    def _register_routes(self):
        """Register all routes for this controller."""
        self.router.get("/sources", response_model=List[Source])(self.get_sources)

    def get_sources(self) -> List[Source]:
        """
        Retrieve all NASA image sources.

        Returns:
            List of all available sources without search filtering
        """
        logger.info("Getting all sources")
        sources = self.sources_service.get_all_sources()
        logger.info(f"Found {len(sources)} sources")
        return sources

