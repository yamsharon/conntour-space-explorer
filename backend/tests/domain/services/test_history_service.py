"""Tests for HistoryService."""

import pytest

from app.domain.models import HistoryResponse, SearchResultHistory, SearchResult
from app.domain.services.history_service import HistoryService
from tests.tests_utils import DummyDB, generate_search_results


@pytest.fixture
def mock_db():
    """Create a mock database for testing."""
    return DummyDB()


@pytest.fixture
def history_service(mock_db):
    """Create a HistoryService instance for testing."""
    return HistoryService(db=mock_db)


def test_add_search_result_history(history_service, mock_db):
    """Test adding a new search result history."""
    query = "test query"
    results = generate_search_results(5)

    history_service.add_search_result_history(query, results)

    assert len(mock_db.search_results_history) == 1
    history_item = mock_db.search_results_history[0]
    assert history_item.query == query
    assert len(history_item.all_search_results) == 5
    # Verify structure: list of dicts with 'id' and 'confidence'
    assert all(isinstance(result, dict) for result in history_item.all_search_results)
    assert all("id" in result and "confidence" in result for result in history_item.all_search_results)
    assert history_item.id is not None
    assert history_item.time_searched is not None


def test_get_history_empty(history_service):
    """Test getting history when there are no items."""
    response = history_service.get_history()

    assert isinstance(response, HistoryResponse)
    assert len(response.items) == 0
    assert response.total == 0


def test_get_history_single_item(history_service, mock_db):
    """Test getting history with a single item."""
    query = "test query"
    results = generate_search_results(3)
    history_service.add_search_result_history(query, results)

    response = history_service.get_history()

    assert response.total == 1
    assert len(response.items) == 1
    assert response.items[0].query == query
    assert len(response.items[0].top_three_images) == 3


def test_get_history_pagination(history_service, mock_db):
    """Test pagination of history items."""
    # Add 5 history items
    for i in range(5):
        history_service.add_search_result_history(f"query {i}", generate_search_results(2))

    # Get first page (limit=2)
    response = history_service.get_history(start_index=0, limit=2)
    assert response.total == 5
    assert len(response.items) == 2

    # Get second page
    response = history_service.get_history(start_index=2, limit=2)
    assert len(response.items) == 2

    # Get third page (partial)
    response = history_service.get_history(start_index=4, limit=2)
    assert len(response.items) == 1


def test_get_history_sorted_by_most_recent(history_service, mock_db):
    """Test that history is sorted by most recent first."""
    # Add items with explicit timestamps to control order

    # Create history items manually to control timestamps (using new format with IDs and confidence)
    results1 = generate_search_results(2)
    results_data1 = [{"id": result.id, "confidence": result.confidence} for result in results1]
    older_item = SearchResultHistory(
        query="older query",
        time_searched="2024-01-01T00:00:00Z",
        all_search_results=results_data1
    )
    results2 = generate_search_results(2)
    results_data2 = [{"id": result.id, "confidence": result.confidence} for result in results2]
    newer_item = SearchResultHistory(
        query="newer query",
        time_searched="2024-01-02T00:00:00Z",
        all_search_results=results_data2
    )

    mock_db.add_search_result_history(older_item)
    mock_db.add_search_result_history(newer_item)

    response = history_service.get_history()

    assert response.total == 2
    # Most recent should be first
    assert response.items[0].query == "newer query"
    assert response.items[1].query == "older query"


def test_get_history_top_three_images(history_service, mock_db):
    """Test that only top three images are returned in response."""
    # Add history with 5 results
    results = generate_search_results(5)
    history_service.add_search_result_history("test query", results)

    response = history_service.get_history()

    assert len(response.items) == 1
    assert len(response.items[0].top_three_images) == 3
    # Verify the top three are the first three results
    assert response.items[0].top_three_images[0].id == results[0].id
    assert response.items[0].top_three_images[1].id == results[1].id
    assert response.items[0].top_three_images[2].id == results[2].id


def test_get_history_less_than_three_results(history_service, mock_db):
    """Test history with less than three results."""
    results = generate_search_results(2)
    history_service.add_search_result_history("test query", results)

    response = history_service.get_history()

    assert len(response.items) == 1
    assert len(response.items[0].top_three_images) == 2


def test_delete_history_item_success(history_service, mock_db):
    """Test successfully deleting a history item."""
    results = generate_search_results(2)
    history_service.add_search_result_history("test query", results)

    history_id = mock_db.search_results_history[0].id
    deleted = history_service.delete_history_item(history_id)

    assert deleted is True
    assert len(mock_db.search_results_history) == 0


def test_delete_history_item_not_found(history_service):
    """Test deleting a non-existent history item."""
    deleted = history_service.delete_history_item("non-existent-id")

    assert deleted is False


def test_delete_history_item_multiple_items(history_service, mock_db):
    """Test deleting one item when multiple exist."""
    # Add multiple items
    for i in range(3):
        history_service.add_search_result_history(f"query {i}", generate_search_results(2))

    target_id = mock_db.search_results_history[1].id
    deleted = history_service.delete_history_item(target_id)

    assert deleted is True
    assert len(mock_db.search_results_history) == 2
    # Verify the correct item was deleted
    remaining_ids = [item.id for item in mock_db.search_results_history]
    assert target_id not in remaining_ids


def test_create_search_results_history_response(history_service, mock_db):
    """Test the method that converts SearchResultHistory to SearchResultHistoryResponse."""
    results = generate_search_results(5)
    # Store as IDs and confidence scores (new format)
    results_data = [{"id": result.id, "confidence": result.confidence} for result in results]
    history = SearchResultHistory(
        id="test-id",
        query="test query",
        time_searched="2024-01-01T00:00:00Z",
        all_search_results=results_data
    )

    response = history_service.create_search_results_history_response(history)

    assert response.id == "test-id"
    assert response.query == "test query"
    assert response.time_searched == "2024-01-01T00:00:00Z"
    assert len(response.top_three_images) == 3
    # Verify that results were reconstructed (they should be SearchResult objects)
    assert all(isinstance(img, SearchResult) for img in response.top_three_images)
    assert response.top_three_images[0].id == results[0].id
    assert response.top_three_images[1].id == results[1].id
    assert response.top_three_images[2].id == results[2].id


def test_get_history_results_success(history_service, mock_db):
    """Test successfully getting history results by ID."""
    results = generate_search_results(5)
    history_service.add_search_result_history("test query", results)
    
    history_id = mock_db.search_results_history[0].id
    retrieved_results = history_service.get_history_results(history_id)
    
    assert len(retrieved_results) == 5
    # Verify that results were reconstructed as SearchResult objects
    assert all(isinstance(result, SearchResult) for result in retrieved_results)
    # Verify IDs match (confidence may differ due to normalization, so we check IDs)
    assert [r.id for r in retrieved_results] == [r.id for r in results]


def test_get_history_results_not_found(history_service):
    """Test getting history results for non-existent ID."""
    with pytest.raises(ValueError, match="History item with ID.*not found"):
        history_service.get_history_results("non-existent-id")
