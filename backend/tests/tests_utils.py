"""Test utilities for the Conntour Space Explorer backend tests."""
from typing import List

from app.domain.models import SearchResultHistory, SearchResult
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
            {
                "id": 3,
                "name": "Mars Rover",
                "type": "Rover",
                "launch_date": "2020-07-30",
                "description": "Mars exploration rover",
                "image_url": "http://image.com/marsrover.jpg",
                "status": "Active",
            },
            {
                "id": 4,
                "name": "Hubble Telescope",
                "type": "Telescope",
                "launch_date": "1990-04-24",
                "description": "Space telescope",
                "image_url": "http://image.com/hubble.jpg",
                "status": "Active",
            },
            {
                "id": 5,
                "name": "ISS",
                "type": "Station",
                "launch_date": "1998-11-20",
                "description": "International Space Station",
                "image_url": "http://image.com/iss.jpg",
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

    def get_sources_by_ids(self, source_ids):
        """Get sources by their IDs (without embeddings).
        
        Args:
            source_ids: List of source IDs to retrieve.
            
        Returns:
            Dictionary mapping source ID to source dict (without embeddings).
        """
        sources_dict = {}
        for source in self.sources:
            source_id = source.get("id")
            if source_id in source_ids:
                source_clean = {k: v for k, v in source.items() if k != EMBEDDING_KEY}
                sources_dict[source_id] = source_clean
        return sources_dict

    def get_all_search_results_history(self):
        """Get all search results history (for SearchService tests)."""
        return self.search_results_history

    def add_search_result_history(self, search_result_history: SearchResultHistory):
        """Add a new search result history (for SearchService tests)."""
        self.search_results_history.append(search_result_history)

    def get_search_result_history_by_id(self, history_id: str) -> SearchResultHistory:
        """Get a search result history by ID (for HistoryService tests).
        
        Args:
            history_id: The ID of the history item to retrieve.
            
        Returns:
            The SearchResultHistory object if found.
            
        Raises:
            ValueError: If the history item is not found.
        """
        for item in self.search_results_history:
            if item.id == history_id:
                return item
        raise ValueError(f"History item with ID {history_id} not found")

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


def generate_search_results(count=1) -> List[SearchResult]:
    return [SearchResult(id=idx, name=f"image-{idx}", type="image", launch_date="2018-06-25T00:00:00Z",
                         description=f"image-{idx}", image_url="http://image.url", status="Active", confidence=0.6) for
            idx in
            range(1, count + 1)]
