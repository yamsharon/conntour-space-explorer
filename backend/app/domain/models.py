import uuid
from typing import Optional, List

from pydantic import BaseModel, Field


class Source(BaseModel):
    """Model representing a NASA image source."""
    id: int
    name: str
    type: str
    launch_date: str
    description: str
    image_url: Optional[str]
    status: str


class SearchResult(Source):
    """Model representing a search result with confidence score."""
    confidence: float


class SearchResultHistory(BaseModel):
    """Model representing a search history result (internal storage)."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str
    time_searched: str
    all_search_results: List[SearchResult]


class SearchResultHistoryResponse(BaseModel):
    """Model representing a search history result response (response to the frontend)."""
    id: str
    query: str
    time_searched: str
    top_three_images: List[SearchResult]


class HistoryResponse(BaseModel):
    """API model representing paginated history response."""
    items: List[SearchResultHistoryResponse]
    total: int
