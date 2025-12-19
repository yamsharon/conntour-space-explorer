"""Test utilities for the Conntour Space Explorer backend tests."""
from app.domain.models import SearchResultHistory
from app.utils.constants import EMBEDDING_KEY


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

        self.search_results_history = []

        if include_embeddings:
            # Add embeddings for search service tests
            self.sources[0][EMBEDDING_KEY] = [0.2, 0.5, 0.7]
            self.sources[1][EMBEDDING_KEY] = [0.9, 0.3, 0.4]

    def get_all_sources(self):
        """Get all sources without embeddings (for SourcesService tests)."""
        return [
            {k: v for k, v in source.items() if k != EMBEDDING_KEY}
            for source in self.sources
        ]

    def get_all_sources_with_embedding(self):
        """Get all sources with embeddings (for SearchService tests)."""
        return self.sources

    def get_all_search_results_history(self):
        """Get all search results history (for SearchService tests)."""
        return self.search_results_history

    def add_search_result_history(self, search_result_history: SearchResultHistory):
        """Add a new search result history (for SearchService tests)."""
        self.search_results_history.append(search_result_history)

    def delete_search_result_history(self, history_id: str) -> bool:
        """Delete a search result history by ID (for HistoryService tests).
        
        Args:
            history_id: The ID of the history item to delete.
            
        Returns:
            True if the item was found and deleted, False otherwise.
        """
        initial_length = len(self.search_results_history)
        self.search_results_history = [
            item for item in self.search_results_history if item.id != history_id
        ]
        return len(self.search_results_history) < initial_length


class DummyLM:
    """A dummy language model for testing."""
    def __init__(self):
        self.model = "dummy_model"
        self.processor = "dummy_processor"
