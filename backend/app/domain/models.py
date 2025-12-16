from typing import Optional

from pydantic import BaseModel


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


