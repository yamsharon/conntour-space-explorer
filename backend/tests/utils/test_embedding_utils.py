import os

import numpy as np

from app.utils import embedding_utils


def test_check_for_cached_embeddings_returns_none_when_no_cache(tmp_path, monkeypatch):
    """Test that check_for_cached_embeddings returns cache_path and None when no cache exists."""
    dummy_path = tmp_path / "not_exist.json"
    dummy_path.touch()  # Create the file so data_path exists

    # Patch the cache path construction to use tmp_path
    original_dirname = os.path.dirname

    def mock_dirname(path):
        if "embedding_utils.py" in str(path) or path == embedding_utils.__file__:
            return str(tmp_path)
        return original_dirname(path)

    monkeypatch.setattr(os.path, "dirname", mock_dirname)

    cache_path, cached_embeddings = embedding_utils.check_for_cached_embeddings(str(dummy_path))
    assert cache_path is not None
    assert isinstance(cache_path, str)
    assert cached_embeddings is None


def test_save_and_load_embeddings_cache(tmp_path):
    """Test saving and loading embeddings cache."""
    embeddings_dict = {
        1: np.array([1.1, 2.2, 3.3], dtype=np.float32),
        2: np.array([4.4, 5.5, 6.6], dtype=np.float32),
    }
    cache_path = str(tmp_path / "cache.pkl")

    # Save embeddings
    embedding_utils.save_embeddings_cache(embeddings_dict, cache_path)

    # Load embeddings
    loaded_embeddings = embedding_utils.load_embeddings_cache(cache_path)

    assert loaded_embeddings is not None
    assert len(loaded_embeddings) == 2
    assert 1 in loaded_embeddings
    assert 2 in loaded_embeddings
    np.testing.assert_allclose(embeddings_dict[1], loaded_embeddings[1])
    np.testing.assert_allclose(embeddings_dict[2], loaded_embeddings[2])


def test_get_image_embedding_from_cache():
    """Test that get_image_embedding returns cached embedding when available."""
    cached_embeddings = {
        1: np.array([0.1, 0.2, 0.3], dtype=np.float32)
    }

    result = embedding_utils.get_image_embedding("model", "processor", cached_embeddings, 1, "http://img.jpg")

    assert isinstance(result, np.ndarray)
    np.testing.assert_allclose(result, np.array([0.1, 0.2, 0.3], dtype=np.float32))


def test_get_image_embedding_generates_new(monkeypatch):
    """Test that get_image_embedding generates new embedding when not in cache."""
    # Patch get_embedding_from_image_url to return a dummy embedding
    monkeypatch.setattr(
        embedding_utils,
        "get_embedding_from_image_url",
        lambda *a, **kw: np.array([0.4, 0.5, 0.6], dtype=np.float32)
    )

    result = embedding_utils.get_image_embedding("model", "processor", None, 0, "http://img.jpg")

    assert isinstance(result, np.ndarray)
    np.testing.assert_allclose(result, np.array([0.4, 0.5, 0.6], dtype=np.float32))
