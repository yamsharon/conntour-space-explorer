from app.infra.db import SpaceDB


class SourcesService:
    """Service for fetching NASA images."""

    def __init__(self, db: SpaceDB):
        self.db = db

    def get_all_sources(self):
        return self.db.get_all_sources()
