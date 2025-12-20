"""Service for managing search history."""
from datetime import datetime, timezone
from typing import List, Dict

from app.domain.models import HistoryResponse, SearchResultHistory, SearchResult, SearchResultHistoryResponse, Source
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
        
        Stores only IDs and confidence scores to save memory.

        Args:
            query (str): The query to search for.
            final_results (List[SearchResult]): The final results.

        Returns:
            None
        """
        logger.info(f"Adding new search result history for query: '{query}'")
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        # Store only IDs and confidence scores
        results_data = [{"id": result.id, "confidence": result.confidence} for result in final_results]
        new_search_result_history: SearchResultHistory = SearchResultHistory(
            query=query,
            time_searched=current_time,
            all_search_results=results_data
        )
        self.db.add_search_result_history(new_search_result_history)
        logger.info(f"Added new search result history for query: '{query}' with {len(results_data)} results")

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
        all_history_responses = [self.create_search_results_history_response(search_results_history) for
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

    def create_search_results_history_response(self, search_results_history: SearchResultHistory) -> SearchResultHistoryResponse:
        """Create a SearchResultHistoryResponse from a SearchResultHistory.
        
        Reconstructs the top 3 SearchResult objects from stored IDs and confidence scores.
        
        Args:
            search_results_history: The history item with stored IDs and confidence scores.
            
        Returns:
            SearchResultHistoryResponse with top 3 full SearchResult objects.
        """
        logger.info(f"Creating SearchResultHistoryResponse for history item with ID: {search_results_history.id}")
        top_three_data = search_results_history.all_search_results[:3]
        top_three_results = self._reconstruct_search_results(top_three_data)
        return SearchResultHistoryResponse(
            id=search_results_history.id,
            query=search_results_history.query,
            time_searched=search_results_history.time_searched,
            top_three_images=top_three_results
        )
    
    def _reconstruct_search_results(self, results_data: List[Dict[str, float]]) -> List[SearchResult]:
        """Reconstruct SearchResult objects from stored IDs and confidence scores.
        
        Args:
            results_data: List of dicts with 'id' and 'confidence' keys.
            
        Returns:
            List of SearchResult objects.
        """
        logger.debug(f"Reconstructing SearchResult objects from stored IDs and confidence scores: {results_data}")
        if not results_data:
            return []
        
        # Get all source IDs we need
        source_ids = [int(result["id"]) for result in results_data]
        
        # Get sources from database
        sources_dict = self.db.get_sources_by_ids(source_ids)
        
        # Reconstruct SearchResult objects
        reconstructed_results = []
        logger.debug(f"Reconstructing {len(results_data)} SearchResult objects")
        for result_data in results_data:
            source_id = int(result_data["id"])
            confidence = result_data["confidence"]
            
            if source_id not in sources_dict:
                logger.warning(f"Source with ID {source_id} not found in database, skipping")
                continue
            
            source_dict = sources_dict[source_id]
            source = Source(**source_dict)
            search_result = SearchResult(
                id=source.id,
                name=source.name,
                type=source.type,
                launch_date=source.launch_date,
                description=source.description,
                image_url=source.image_url,
                status=source.status,
                confidence=confidence
            )
            reconstructed_results.append(search_result)
        
        logger.debug(f"Reconstructed {len(reconstructed_results)} SearchResult objects")
        return reconstructed_results

    def get_history_results(self, history_id: str) -> List[SearchResult]:
        """Get the full search results for a specific history item.
        
        Reconstructs full SearchResult objects from stored IDs and confidence scores.

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
                # Reconstruct full SearchResult objects from stored IDs and confidence scores
                results = self._reconstruct_search_results(history_item.all_search_results)
                logger.info(f"Reconstructed {len(results)} SearchResult objects")
                return results
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
