import numpy as np


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two normalized vectors."""
    # Since embeddings are normalized, cosine similarity is just dot product
    dot_product = np.dot(vec1, vec2)
    return float(np.clip(dot_product, -1.0, 1.0))
