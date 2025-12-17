"""Test utilities for the Conntour Space Explorer backend tests."""


class DummyDB:
    """Mock database for testing that implements both get_all_sources methods."""

    def __init__(self, include_embeddings: bool = False):
        """
        Initialize the DummyDB with test data.

        Args:
            include_embeddings: If True, sources will include embedding data
        """
        self.sources = [
            {
                "id": 1,
                "name": "Apollo 11",
                "type": "Mission",
                "launch_date": "1969-07-16",
                "description": "First Moon landing",
                "image_url": "http://image.com/apollo11.jpg",
                "status": "Retired",
            },
            {
                "id": 2,
                "name": "Voyager 1",
                "type": "Probe",
                "launch_date": "1977-09-05",
                "description": "Interstellar probe",
                "image_url": "http://image.com/voyager1.jpg",
                "status": "Active",
            },
        ]

        if include_embeddings:
            # Add embeddings for search service tests
            self.sources[0]["embedding"] = [0.2, 0.5, 0.7]
            self.sources[1]["embedding"] = [0.9, 0.3, 0.4]

    def get_all_sources(self):
        """Get all sources without embeddings (for SourcesService tests)."""
        return [
            {k: v for k, v in source.items() if k != "embedding"}
            for source in self.sources
        ]

    def get_all_sources_with_embedding(self):
        """Get all sources with embeddings (for SearchService tests)."""
        return self.sources

