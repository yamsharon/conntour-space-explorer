"""Embedding service for generating text embeddings using sentence-transformers."""
import os
import pickle
from io import BytesIO
from typing import Optional, Dict

import numpy as np
import requests
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

from app.utils.constants import EMBEDDING_CACHE
from app.utils.logger import logger


def get_embedding_from_image_url(model: CLIPModel, processor: CLIPProcessor, image_url: str):
    """
    Get an embedding from an image URL using a language model.

    Args:
        model (CLIPModel): The language model to use for generating embeddings.
        processor (CLIPProcessor): The processor to use for generating embeddings.
        image_url (str): The URL of the image to get an embedding from.
    """
    logger.debug(f"Getting embedding from image URL: {image_url}")
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content)).convert("RGB")

    # Process image and get features
    inputs = processor(images=img, return_tensors="pt")
    with torch.no_grad():
        # Extract the visual features (the vector)
        image_features = model.get_image_features(**inputs)

    # Store as a list, so it's JSON serializable later if needed
    embedding = image_features.numpy().flatten()
    logger.info(f"Generated embedding for image {image_url} - {embedding.shape}")
    return embedding


def save_embeddings_cache(embeddings: Dict[int, np.ndarray], cache_path: str):
    """
    Save embeddings to a cache file.
    
    Args:
        embeddings: Dictionary mapping source IDs to embedding arrays
        cache_path: Path to the cache file
    """
    try:
        logger.info("Saving embedding to cache...")
        # Ensure directory exists
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)

        # Convert numpy arrays to list for JSON serialization, or use pickle
        # Using pickle for better performance with numpy arrays
        with open(cache_path, 'wb') as f:
            pickle.dump(embeddings, f)

        logger.info(f"Saved {len(embeddings)} embeddings to cache: {cache_path}")
    except Exception as e:
        logger.error(f"Failed to save embeddings cache: {e}")


def load_embeddings_cache(cache_path: str) -> Optional[Dict[int, np.ndarray]]:
    """
    Load embeddings from a cache file.
    
    Args:
        cache_path: Path to the cache file
        
    Returns:
        Dictionary mapping source IDs to embedding arrays, or None if cache doesn't exist
    """
    logger.info("Loading embedding from cache")
    if not os.path.exists(cache_path):
        return None

    try:
        with open(cache_path, 'rb') as f:
            embeddings = pickle.load(f)

        logger.info(f"Loaded {len(embeddings)} embeddings from cache: {cache_path}")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to load embeddings cache: {e}")
        return None


def is_cache_valid(cache_path: str, data_path: str) -> bool:
    """
    Check if the cache is valid by comparing modification times.
    
    Args:
        cache_path: Path to the cache file
        data_path: Path to the data file
        
    Returns:
        True if cache exists and is newer than data file, False otherwise
    """
    logger.info("Checking if the cache is valid")
    if not os.path.exists(cache_path):
        return False

    if not os.path.exists(data_path):
        return False

    try:
        cache_mtime = os.path.getmtime(cache_path)
        data_mtime = os.path.getmtime(data_path)
        return cache_mtime >= data_mtime
    except Exception as e:
        logger.error(f"Error checking cache validity: {e}")
        return False


def check_for_cached_embeddings(data_path):
    """
    Check for cached embeddings and return the cache path and embeddings.

    Args:
        data_path (str): The path to the data file.
    """
    logger.info("Checking for cached embeddings")
    cache_path = os.path.join(os.path.dirname(__file__), EMBEDDING_CACHE)
    cached_embeddings = None
    if is_cache_valid(cache_path, data_path):
        cached_embeddings = load_embeddings_cache(cache_path)
        if cached_embeddings:
            logger.info(f"Using cached embeddings for {len(cached_embeddings)} sources")
    return cache_path, cached_embeddings


def calculate_image_and_text_similarity(image_vec, text_vec):
    image_vec = image_vec / image_vec.norm(dim=-1, keepdim=True)
    text_vec = text_vec / text_vec.norm(dim=-1, keepdim=True)
    # Calculate the cosine similarity score
    score = (text_vec @ image_vec.t()).item()
    return score


def get_image_embedding(model, processor, cached_embeddings, idx, image_url):
    """
    Get the image embedding for a source.

    Args:
        model (transformers.CLIPModel): The model to use for generating embeddings.
        processor (transformers.CLIPProcessor): The processor to use for encoding text.
        cached_embeddings (dict): The cached embeddings.
        idx (int): The index of the source.
        image_url (str): The URL of the image.
    """
    logger.debug(f"Getting image embedding for source {idx}")
    # Try to load embedding from cache, otherwise generate it
    if cached_embeddings and idx in cached_embeddings:
        embedding = cached_embeddings[idx]
        logger.debug(f"Loaded cached embedding for source {idx}")
    else:
        embedding = get_embedding_from_image_url(model, processor, image_url)
        logger.debug(f"Generated embedding for source {idx}")
    return embedding
