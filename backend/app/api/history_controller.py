"""Controller for handling history-related API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from app.api.dependencies import get_history_service
from app.domain.models import HistoryResponse, SearchResult
from app.domain.services.history_service import HistoryService
from app.utils.logger import logger


class HistoryController:
    """Controller for managing history endpoints."""

    def __init__(self):
        """Initialize the HistoryController."""
        logger.info("Initializing HistoryController")
        self.router = APIRouter(prefix="/api", tags=["history"])

        # Register routes
        self.router.get("/history", response_model=HistoryResponse)(self.get_history)
        self.router.get("/history/{history_id}/results", response_model=List[SearchResult])(self.get_history_results)
        self.router.delete("/history/{history_id}")(self.delete_history_item)

    @staticmethod
    def get_history(
            startIndex: int = Query(0, description="Starting index for pagination", ge=0),
            limit: int = Query(10, description="Number of items per page", ge=1, le=100),
            history_service: HistoryService = Depends(get_history_service)
    ) -> HistoryResponse:
        """
        Get paginated search history.

        Args:
            startIndex: Starting index for pagination (default: 0)
            limit: Maximum number of items to return (default: 10, max: 100)
            history_service: Injected history service

        Returns:
            HistoryResponse containing paginated items and total count
        """
        logger.info(f"Getting history: startIndex={startIndex}, limit={limit}")
        response = history_service.get_history(start_index=startIndex, limit=limit)
        logger.info(f"Returning {len(response.items)} items (total: {response.total})")
        return response

    @staticmethod
    def get_history_results(
            history_id: str,
            history_service: HistoryService = Depends(get_history_service)
    ) -> List[SearchResult]:
        """
        Get the full search results for a specific history item.

        Args:
            history_id: UUID of the history item
            history_service: Injected history service

        Returns:
            List of SearchResult objects for the history item

        Raises:
            404: If the history item is not found
        """
        logger.info(f"Getting history results for ID: {history_id}")
        try:
            results = history_service.get_history_results(history_id)
            logger.info(f"Returning {len(results)} results for history ID: {history_id}")
            return results
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

    @staticmethod
    def delete_history_item(
            history_id: str,
            history_service: HistoryService = Depends(get_history_service)
    ) -> Response:
        """
        Delete a specific history item by ID.

        Args:
            history_id: UUID of the history item to delete
            history_service: Injected history service

        Returns:
            204 No Content if successful, 404 if not found
        """
        logger.info(f"Deleting history item: {history_id}")
        deleted = history_service.delete_history_item(history_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"History item with ID {history_id} not found"
            )

        logger.info(f"Successfully deleted history item: {history_id}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
