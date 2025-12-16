"""In-memory database for NASA space images with vector embeddings."""

import json
import os
from typing import Dict, List, Tuple

import numpy as np

from app.infra.language_model import LanguageModel
from app.utils.embedding_utils import generate_embeddings_batch, get_similarity, map_similarity_to_confidence
from app.utils.logger import logger


class SpaceDB:
    """In-memory database for NASA space images with vector embeddings."""

    def __init__(self, lm: LanguageModel):
        logger.info("Initializing SpaceDB")
        self.lm = lm

        # Load data
        data_path = os.path.join(os.path.dirname(__file__), "data/mock_data.json")
        with open(data_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Parse sources
        self._sources = []
        items = json_data.get("collection", {}).get("items", [])
        texts_for_embedding = []

        for idx, item in enumerate(items, start=1):
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
            keywords = data.get("keywords", [])

            source = {
                "id": idx,
                "name": name,
                "type": data.get("media_type", "unknown"),
                "launch_date": data.get("date_created", ""),
                "description": description,
                "image_url": image_url,
                "status": "Active",
            }
            self._sources.append(source)

            # Use only keywords for embedding (or fallback to name if no keywords)
            if keywords:
                text_for_embedding = ", ".join(keywords).strip()
            else:
                # Fallback to name if no keywords available
                text_for_embedding = name.strip() if name else ""

            texts_for_embedding.append(text_for_embedding)

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts_for_embedding)} sources...")
        embeddings = generate_embeddings_batch(self.lm.model, texts_for_embedding)

        # Store embeddings
        for idx, embedding in enumerate(embeddings):
            if embedding is not None:
                self._sources[idx]["embedding"] = embedding
            else:
                logger.warning(f"Failed to generate embedding for source {idx + 1}")

        logger.info(
            f"SpaceDB initialized: {len(self._sources)} sources, "
            f"{sum(1 for s in self._sources if 'embedding' in s)} with embeddings"
        )

    def get_all_sources(self) -> List[Dict]:
        """Get all sources without embeddings."""
        return [
            {k: v for k, v in source.items() if k != "embedding"}
            for source in self._sources
        ]

    def search_by_embedding(
            self, query_embedding: np.ndarray, limit: int = 15
    ) -> List[Tuple[Dict, float]]:
        """
        Search sources using vector similarity.
        
        Returns list of (source_dict, confidence_score) tuples sorted by confidence descending.
        """
        # Normalize query embedding
        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            logger.error("Query embedding has zero norm")
            return []
        query_embedding = query_embedding / query_norm

        # Calculate similarities
        results = []
        for source in self._sources:
            similarity = get_similarity(source, query_embedding)

            # Only include results with meaningful similarity
            if similarity > 0.0:
                results.append((source, float(similarity)))

        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)

        # Apply confidence scaling: map similarity [min, max] to confidence [0.2, 1.0]
        if results:
            results = map_similarity_to_confidence(results)

        return results[:limit]
