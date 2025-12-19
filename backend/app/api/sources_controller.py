"""Controller for handling sources-related API endpoints."""

from typing import List

from fastapi import APIRouter, Depends

from app.api.dependencies import get_sources_service
from app.domain.models import Source
from app.domain.services.sources_service import SourcesService
from app.utils.logger import logger


class SourcesController:
    """Controller for managing sources endpoints."""

    def __init__(self):
        """Initialize the SourcesController."""
        logger.info("Initializing SourcesController")
        self.router = APIRouter(prefix="/api", tags=["sources"])
        self.router.get("/sources", response_model=List[Source])(self.get_sources)

    def get_sources(
        self,
        sources_service: SourcesService = Depends(get_sources_service)
    ) -> List[Source]:
        """
        Retrieve all NASA image sources.

        Args:
            sources_service: Injected sources service

        Returns:
            List of all available sources
        """
        logger.info("Getting all sources")
        sources = sources_service.get_all_sources()
        logger.info(f"Found {len(sources)} sources")
        return sources

