"""Embedding service for generating text embeddings using sentence-transformers."""

from typing import List, Optional, Dict

import numpy as np
from sentence_transformers import SentenceTransformer

from app.infra.language_model import LanguageModel
from app.utils import vectors_utils
from app.utils.logger import logger


def generate_embedding(model: SentenceTransformer, text: str) -> Optional[np.ndarray]:
    """Generate a normalized embedding vector for the given text."""
    if not text or not text.strip():
        return None

    try:
        # sentence-transformers automatically normalizes embeddings
        embedding = model.encode(
            text.strip(),
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embedding.astype(np.float32)
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None


def generate_embeddings_batch(
        model: SentenceTransformer, texts: List[str], batch_size: int = 32
) -> List[Optional[np.ndarray]]:
    """Generate embeddings for a batch of texts."""
    if not texts:
        return []

    valid_texts = [t.strip() for t in texts if t and t.strip()]
    if not valid_texts:
        return [None] * len(texts)

    try:
        # Generate embeddings for valid texts
        embeddings = model.encode(
            valid_texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=batch_size,
            show_progress_bar=False,
        )

        # Map back to original list (handling empty texts)
        final_results = []
        text_idx = 0
        for original_text in texts:
            if original_text and original_text.strip():
                final_results.append(embeddings[text_idx].astype(np.float32))
                text_idx += 1
            else:
                final_results.append(None)

        logger.info(f"Generated {len(embeddings)} embeddings")
        return final_results
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}")
        return [None] * len(texts)


def get_similarity(source: Dict, query_embedding: List):
    # Making sure the image was processed
    if "embedding" not in source:
        return None

    source_embedding = source["embedding"]
    source_norm = np.linalg.norm(source_embedding)
    if source_norm == 0:
        return None

    source_embedding = source_embedding / source_norm
    similarity = vectors_utils.cosine_similarity(
        query_embedding, source_embedding
    )

    return similarity


def map_similarity_to_confidence(results):
    sim_values = [sim for _, sim in results]
    min_sim = min(sim_values)
    max_sim = max(sim_values)
    sim_range = max_sim - min_sim
    if sim_range > 0.0001:
        # Linear scaling: min_sim -> 0.2, max_sim -> 1.0
        scaled_results = []
        for source, sim in results:
            confidence = 0.2 + 0.8 * ((sim - min_sim) / sim_range)
            scaled_results.append((source, confidence))
        results = scaled_results
    else:
        # All similarities are the same - use rank-based confidence
        scaled_results = []
        for idx, (source, _) in enumerate(results):
            confidence = 1.0 - (idx * 0.05)  # Decrease by 5% per rank
            scaled_results.append((source, max(0.1, confidence)))
        results = scaled_results
    return results
