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
    """Model representing a search history result."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str
    time_searched: str
    top_three_images_urls: List[str]
