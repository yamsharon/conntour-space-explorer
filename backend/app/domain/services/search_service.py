"""Search service for semantic image search using embeddings."""
from typing import List, Dict

import torch

from app.domain.models import SearchResult, Source
from app.domain.services.history_service import HistoryService
from app.infra.db import SpaceDB
from app.infra.language_model import LanguageModel
from app.utils.constants import EMBEDDING_KEY
from app.utils.embedding_utils import calculate_image_and_text_similarity
from app.utils.logger import logger


def normalize_results(results: List[SearchResult]):
    """
    Normalize the confidence scores for a list of SearchResult objects.

    This function rescales each score to a value between 0.2 and 1.0,
    where the minimum confidence across all results maps to 0.2 and
    the maximum confidence maps to 1.0. If all scores are identical,
    all results will be assigned a confidence of 0.6.

    Args:
        results (List[SearchResult]): List of SearchResult objects with confidence attributes.

    Returns:
        List[SearchResult]: List of SearchResult objects with normalized confidence values.
    """
    logger.info("Normalizing search results between 0.2 to 1.0")
    confidence_values = [result.confidence for result in results]
    min_confidence = min(confidence_values)
    max_confidence = max(confidence_values)
    confidence_range = max_confidence - min_confidence
    logger.debug(
        f"Confidence range: {confidence_range}, min_confidence: {min_confidence}, max_confidence: {max_confidence}")

    scaled_results = []
    for result in results:
        if confidence_range == 0:  # If the confidence range is 0, we return a default confidence of 0.6
            result.confidence = 0.6
        else:  # If the confidence range is not 0, we scale the confidence
            logger.debug(f"Scaling confidence for result: {result.name}")
            norm_confidence = result.confidence
            logger.debug(f"Normalized confidence: {norm_confidence}")
            result.confidence = 0.2 + 0.8 * ((norm_confidence - min_confidence) / confidence_range)
        scaled_results.append(result)
    return scaled_results


def calculate_similarity_for_one_source(source_dict, text_vec):
    """
    Calculate similarity between an image and a text vector.

    Args:
        source_dict (dict): The source dictionary.
        text_vec (torch.Tensor): The text vector.

    Returns:
        SearchResult: The search result.
    """
    # Calculate Similarity between an image and a text vector
    image_vec = torch.tensor(source_dict[EMBEDDING_KEY])
    score = calculate_image_and_text_similarity(image_vec, text_vec)
    logger.debug(f"Similarity score: {score}")
    source_clean = {k: v for k, v in source_dict.items() if k != EMBEDDING_KEY}
    source_dict = Source(**source_clean)
    return SearchResult(
        id=source_dict.id,
        name=source_dict.name,
        type=source_dict.type,
        launch_date=source_dict.launch_date,
        description=source_dict.description,
        image_url=source_dict.image_url,
        status=source_dict.status,
        confidence=round(score * 100, 2),
    )


class SearchService:
    """Service for performing semantic search over NASA images."""

    def __init__(self, db: SpaceDB, lm: LanguageModel, history_service: HistoryService):
        """Initialize the SearchService."""
        logger.info("Initializing SearchService")
        self.db = db
        self.lm = lm
        self.history_service = history_service

    def search(self, query: str, limit: int = 15) -> List[SearchResult]:
        """Perform semantic search using vector embeddings.

        Args:
            query (str): The query to search for.
            limit (int): The maximum number of results to return.

        Returns:
            List[SearchResult]: List of SearchResult objects with normalized confidence values.
        """
        logger.info(f"Searching for: '{query}' with limit of {limit} results")

        # Check if the query is valid
        if not query or not query.strip():
            return []

        # Encode the search text
        inputs = self.lm.processor(text=[query], return_tensors="pt", padding=True)
        with torch.no_grad():
            text_features: torch.Tensor = self.lm.model.get_text_features(**inputs)

        results = []
        # Convert text features to a Torch tensor for comparison
        text_vec = text_features.clone().detach()

        all_sources: List[Dict] = self.db.get_all_sources_with_embedding()

        logger.debug(f"Found {len(all_sources)} sources")
        for source_dict in all_sources:
            if source_dict[EMBEDDING_KEY] is None:
                continue
            search_result = calculate_similarity_for_one_source(source_dict, text_vec)
            results.append(search_result)

        normalized_results = normalize_results(results)

        # Sort by similarity descending
        normalized_results.sort(key=lambda x: x.confidence, reverse=True)
        logger.info(f"Found {len(normalized_results)} results")

        self.history_service.add_search_result_history(query, normalized_results)

        return normalized_results[:limit]
