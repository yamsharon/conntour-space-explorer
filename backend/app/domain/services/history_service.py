"""Service for managing search history."""
from datetime import datetime, timezone
from typing import List

from app.domain.models import HistoryResponse, SearchResultHistory, SearchResult, SearchResultHistoryResponse
from app.infra.db import SpaceDB
from app.utils.logger import logger


class HistoryService:
    """Service for managing search history."""

    def __init__(self, db: SpaceDB):
        """Initialize the HistoryService.

        Args:
            db: The database instance for accessing history data.
        """
        logger.info("Initializing HistoryService")
        self.db = db

    def add_search_result_history(self, query: str, final_results: List[SearchResult]) -> None:
        """
        Add a new search result history to the database.

        Args:
            query (str): The query to search for.
            final_results (List[SearchResult]): The final results.

        Returns:
            None
        """
        logger.info(f"Adding new search result history for query: '{query}'")
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        new_search_result_history: SearchResultHistory = SearchResultHistory(
            query=query,
            time_searched=current_time,
            all_search_results=final_results
        )
        self.db.add_search_result_history(new_search_result_history)
        logger.info(f"Added new search result history for query: '{query}'")

    def get_history(self, start_index: int = 0, limit: int = 10) -> HistoryResponse:
        """Get paginated search history, sorted by most recent first.

        Args:
            start_index: Starting index for pagination.
            limit: Maximum number of items to return.

        Returns:
            HistoryResponse containing paginated items and total count.
        """
        logger.info(f"Getting history: start_index={start_index}, limit={limit}")
        all_history = self.db.get_all_search_results_history()
        all_history_responses = [HistoryService.create_search_results_history_response(search_results_history) for
                                 search_results_history in all_history]
        total = len(all_history)

        # Sort by time_searched in descending order (most recent first)
        sorted_history = sorted(
            all_history_responses,
            key=lambda x: x.time_searched,
            reverse=True
        )

        # Apply pagination
        items = sorted_history[start_index:start_index + limit]

        logger.info(f"Returning {len(items)} history items (total: {total})")
        return HistoryResponse(items=items, total=total)

    @staticmethod
    def create_search_results_history_response(search_results_history: SearchResultHistory):
        return SearchResultHistoryResponse(
            id=search_results_history.id,
            query=search_results_history.query,
            time_searched=search_results_history.time_searched,
            top_three_images=search_results_history.all_search_results[:3]
        )

    def get_history_results(self, history_id: str) -> List[SearchResult]:
        """Get the full search results for a specific history item.

        Args:
            history_id: The ID of the history item.

        Returns:
            List of SearchResult objects for the history item.

        Raises:
            ValueError: If the history item is not found.
        """
        logger.info(f"Getting history results for ID: {history_id}")
        all_history = self.db.get_all_search_results_history()
        for history_item in all_history:
            if history_item.id == history_id:
                logger.info(f"Found history item with {len(history_item.all_search_results)} results")
                return history_item.all_search_results
        logger.warning(f"History item with ID {history_id} not found")
        raise ValueError(f"History item with ID {history_id} not found")

    def delete_history_item(self, history_id: str) -> bool:
        """Delete a history item by ID.

        Args:
            history_id: The ID of the history item to delete.

        Returns:
            True if the item was found and deleted, False otherwise.
        """
        logger.info(f"Deleting history item with ID: {history_id}")
        deleted = self.db.delete_search_result_history(history_id)
        if deleted:
            logger.info(f"Successfully deleted history item: {history_id}")
        else:
            logger.warning(f"History item not found: {history_id}")
        return deleted
