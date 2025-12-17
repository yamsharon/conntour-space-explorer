from app.infra.db import SpaceDB
from app.utils.logger import logger


class SourcesService:
    """Service for fetching NASA images."""

    def __init__(self, db: SpaceDB):
        """Initialize the SourcesService."""
        logger.info("Initializing SourcesService")
        self.db = db

    def get_all_sources(self):
        """Get all sources from the database."""
        logger.info("Getting all sources")
        sources = self.db.get_all_sources()
        logger.info(f"Found {len(sources)} sources")
        return sources
