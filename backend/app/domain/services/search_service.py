"""Search service for semantic image search using embeddings."""

from typing import List

from app.domain.models import SearchResult, Source
from app.infra.db import SpaceDB
from app.infra.language_model import LanguageModel
from app.utils.embedding_utils import generate_embedding
from app.utils.logger import logger


class SearchService:
    """Service for performing semantic search over NASA images."""

    def __init__(self, db: SpaceDB, lm: LanguageModel):
        self.db = db
        self.lm = lm

    def search(self, query: str, limit: int = 15) -> List[SearchResult]:
        """Perform semantic search using vector embeddings."""
        if not query or not query.strip():
            return []

        query_text = query.strip()
        logger.info(f"Searching for: '{query_text}'")

        # Generate query embedding
        query_embedding = generate_embedding(self.lm.model, query_text)
        if query_embedding is None:
            logger.error("Failed to generate query embedding")
            return []

        # Search
        search_results = self.db.search_by_embedding(query_embedding, limit=limit)

        # Convert to SearchResult models
        results = []
        for source_dict, confidence in search_results:
            source_clean = {k: v for k, v in source_dict.items() if k != "embedding"}
            source = Source(**source_clean)
            search_result = SearchResult(
                id=source.id,
                name=source.name,
                type=source.type,
                launch_date=source.launch_date,
                description=source.description,
                image_url=source.image_url,
                status=source.status,
                confidence=confidence,
            )
            results.append(search_result)

        logger.info(f"Found {len(results)} results")
        return results
