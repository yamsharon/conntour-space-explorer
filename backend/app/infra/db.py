"""In-memory database for NASA space images with vector embeddings."""

import json
import os
from typing import Dict, List

from tqdm import tqdm

from app.domain.models import SearchResultHistory
from app.infra.language_model import LanguageModel
from app.utils.constants import MOCK_DATA_JSON, EMBEDDING_KEY
from app.utils.embedding_utils import (
    save_embeddings_cache,
    check_for_cached_embeddings, get_image_embedding
)
from app.utils.logger import logger


class SpaceDB:
    """In-memory database for NASA space images with vector embeddings."""

    def __init__(self, lm: LanguageModel):
        """Initialize the SpaceDB."""
        logger.info("Initializing SpaceDB")
        self._lm: LanguageModel = lm
        self._search_results_history: List[SearchResultHistory] = []

        # Load data
        data_path = os.path.join(os.path.dirname(__file__), MOCK_DATA_JSON)
        with open(data_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Parse sources
        self._sources = []
        items = json_data.get("collection", {}).get("items", [])

        cache_path, cached_embeddings = check_for_cached_embeddings(data_path)

        # Prepare embeddings dict for saving
        embeddings_to_cache = {}

        logger.info(f"Processing {len(items)} sources")
        for idx, item in enumerate(tqdm(items, desc="Processing sources"), start=1):
            source = self.process_one_source(cached_embeddings, embeddings_to_cache, idx, item)
            self._sources.append(source)

        # Save embeddings to cache if we generated any new ones
        if not cached_embeddings or len(embeddings_to_cache) != len(cached_embeddings):
            save_embeddings_cache(embeddings_to_cache, cache_path)

        logger.info(
            f"SpaceDB initialized: {len(self._sources)} sources, "
            f"{sum(1 for s in self._sources if 'embedding' in s)} with embeddings"
        )

    def process_one_source(self, cached_embeddings, embeddings_to_cache, idx, item):
        """
        Process one source and return a dictionary with the source data with the embedding.

        Args:
            cached_embeddings (dict): The cached embeddings.
            embeddings_to_cache (dict): The embeddings to cache.
            idx (int): The index of the source.
            item (dict): The source item.

        Returns:
            dict: The source data with the embedding.
        """
        logger.debug(f"Processing source {idx}")
        data = item.get("data", [{}])[0]
        links = item.get("links", [])
        # Find image URL
        image_url = None
        for link in links:
            if link.get("render") == "image":
                image_url = link.get("href")
                break
        name = data.get("title", f"NASA Item {idx}")
        description = data.get("description", "")
        embedding = get_image_embedding(self._lm.model, self._lm.processor, cached_embeddings, idx, image_url)
        embeddings_to_cache[idx] = embedding
        source = {
            "id": idx,
            "name": name,
            "type": data.get("media_type", "unknown"),
            "launch_date": data.get("date_created", ""),
            "description": description,
            "image_url": image_url,
            "status": "Active",
            EMBEDDING_KEY: embedding
        }
        return source

    def get_all_sources(self) -> List[Dict]:
        """Get all sources without embeddings."""
        logger.info("Getting all sources without embeddings")
        return [
            {k: v for k, v in source.items() if k != EMBEDDING_KEY}
            for source in self._sources
        ]

    def get_all_sources_with_embedding(self) -> List[Dict]:
        """Get all sources with embeddings."""
        logger.info("Getting all sources with embeddings")
        return self._sources

    def get_all_search_results_history(self):
        """Get all search history results."""
        logger.info("Getting all search history results")
        return self._search_results_history

    def add_search_result_history(self, search_result_history: SearchResultHistory):
        """Append a new search result history."""
        logger.info("Appending a new search result history")
        self._search_results_history.append(search_result_history)

    def delete_search_result_history(self, history_id: str) -> bool:
        """Delete a search result history by ID.
        
        Args:
            history_id: The ID of the history item to delete.
            
        Returns:
            True if the item was found and deleted, False otherwise.
        """
        logger.info(f"Deleting search result history with ID: {history_id}")
        initial_length = len(self._search_results_history)
        self._search_results_history = [
            item for item in self._search_results_history if item.id != history_id
        ]
        deleted = len(self._search_results_history) < initial_length
        if deleted:
            logger.info(f"Successfully deleted history item with ID: {history_id}")
        else:
            logger.warning(f"History item with ID {history_id} not found")
        return deleted
