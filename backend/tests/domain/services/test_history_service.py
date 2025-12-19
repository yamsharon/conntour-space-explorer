"""Tests for HistoryService."""

import pytest

from app.domain.models import HistoryResponse, SearchResult, SearchResultHistory
from app.domain.services.history_service import HistoryService
from tests.tests_utils import DummyDB


@pytest.fixture
def mock_db():
    """Create a mock database for testing."""
    return DummyDB()


@pytest.fixture
def history_service(mock_db):
    """Create a HistoryService instance for testing."""
    return HistoryService(db=mock_db)


def test_add_search_result_history_stores_only_top_three(history_service, mock_db):
    """Test that only top 3 results are stored in history."""
    query = "test query"
    results = [
        SearchResult(
            id=i,
            name=f"Item {i}",
            type="Type",
            launch_date="2020-01-01",
            description="Description",
            image_url=f"http://image.com/item{i}.jpg",
            status="Active",
            confidence=0.9 - i * 0.1
        )
        for i in range(1, 6)  # 5 results
    ]

    history_service.add_search_result_history(query, results)

    history = mock_db.get_all_search_results_history()
    assert len(history) == 1
    assert len(history[0].top_three_images_urls) == 3
    assert history[0].top_three_images_urls[0] == "http://image.com/item1.jpg"
    assert history[0].top_three_images_urls[1] == "http://image.com/item2.jpg"
    assert history[0].top_three_images_urls[2] == "http://image.com/item3.jpg"


def test_get_history_returns_paginated_results(history_service, mock_db):
    """Test that get_history returns paginated results correctly."""
    # Add 5 history items
    for i in range(5):
        history_item = SearchResultHistory(
            query=f"query {i}",
            time_searched="2020-01-01T00:00:00Z",
            top_three_images_urls=[f"http://image.com/img{i}.jpg"]
        )
        mock_db.add_search_result_history(history_item)

    # Get first page (limit=2)
    response = history_service.get_history(start_index=0, limit=2)
    assert isinstance(response, HistoryResponse)
    assert response.total == 5
    assert len(response.items) == 2
    assert response.items[0].query == "query 0"
    assert response.items[1].query == "query 1"

    # Get second page
    response = history_service.get_history(start_index=2, limit=2)
    assert len(response.items) == 2
    assert response.items[0].query == "query 2"
    assert response.items[1].query == "query 3"

    # Get last page
    response = history_service.get_history(start_index=4, limit=2)
    assert len(response.items) == 1
    assert response.items[0].query == "query 4"


def test_get_history_returns_empty_when_no_history(history_service):
    """Test that get_history returns empty list when no history exists."""
    response = history_service.get_history()
    assert isinstance(response, HistoryResponse)
    assert response.total == 0
    assert len(response.items) == 0


def test_get_history_handles_start_index_beyond_total(history_service, mock_db):
    """Test that get_history handles start_index beyond total correctly."""
    # Add 2 history items
    for i in range(2):
        history_item = SearchResultHistory(
            query=f"query {i}",
            time_searched="2020-01-01T00:00:00Z",
            top_three_images_urls=[f"http://image.com/img{i}.jpg"]
        )
        mock_db.add_search_result_history(history_item)

    # Request beyond available items
    response = history_service.get_history(start_index=10, limit=5)
    assert response.total == 2
    assert len(response.items) == 0


def test_delete_history_item_removes_item_by_id(history_service, mock_db):
    """Test that delete_history_item removes the correct item."""
    # Add 3 history items
    history_items = []
    for i in range(3):
        history_item = SearchResultHistory(
            query=f"query {i}",
            time_searched="2020-01-01T00:00:00Z",
            top_three_images_urls=[f"http://image.com/img{i}.jpg"]
        )
        mock_db.add_search_result_history(history_item)
        history_items.append(history_item)

    # Delete middle item
    deleted = history_service.delete_history_item(history_items[1].id)

    assert deleted is True
    remaining = mock_db.get_all_search_results_history()
    assert len(remaining) == 2
    assert remaining[0].id == history_items[0].id
    assert remaining[1].id == history_items[2].id


def test_delete_history_item_returns_false_when_not_found(history_service, mock_db):
    """Test that delete_history_item returns False when item not found."""
    # Add one history item
    history_item = SearchResultHistory(
        query="test query",
        time_searched="2020-01-01T00:00:00Z",
        top_three_images_urls=["http://image.com/img.jpg"]
    )
    mock_db.add_search_result_history(history_item)

    # Try to delete non-existent item
    deleted = history_service.delete_history_item("non-existent-id")

    assert deleted is False
    remaining = mock_db.get_all_search_results_history()
    assert len(remaining) == 1


def test_delete_history_item_handles_empty_history(history_service):
    """Test that delete_history_item handles empty history correctly."""
    deleted = history_service.delete_history_item("some-id")
    assert deleted is False
