from typing import List

from app.domain.models import Source
from app.infra.db import SpaceDB
from app.utils.logger import logger


class SourcesService:
    """Service for fetching NASA images."""

    def __init__(self, db: SpaceDB):
        """Initialize the SourcesService."""
        logger.info("Initializing SourcesService")
        self.db = db

    def get_all_sources(self) -> List[Source]:
        """Get all sources from the database."""
        logger.info("Getting all sources")
        sources_dict = self.db.get_all_sources()
        sources = [Source(**source) for source in sources_dict]
        logger.info(f"Found {len(sources)} sources")
        return sources
