import pytest

from app.infra.db import SpaceDB
from app.utils.constants import EMBEDDING_KEY
from tests.tests_utils import DummyLM


@pytest.fixture
def sample_json_data(tmp_path):
    """Create a temporary mock_data.json file for testing."""
    data = {
        "collection": {
            "items": [
                {
                    "data": [{
                        "title": "Test Source 1",
                        "media_type": "image",
                        "date_created": "2020-01-01T00:00:00Z",
                        "description": "Desc 1"
                    }],
                    "links": [{"render": "image", "href": "http://example.com/img1.jpg"}]
                },
                {
                    "data": [{
                        "title": "Test Source 2",
                        "media_type": "image",
                        "date_created": "2021-01-01T00:00:00Z",
                        "description": "Desc 2"
                    }],
                    "links": [{"render": "image", "href": "http://example.com/img2.jpg"}]
                }
            ]
        }
    }
    import json
    # Overwrite MOCK_DATA_JSON to point to our temporary file
    mock_json = tmp_path / "mock_data.json"
    with open(mock_json, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return mock_json


@pytest.fixture(autouse=True)
def patch_mock_data_json(monkeypatch, sample_json_data):
    """Patch the data file path to use the temporary test file."""
    from app.utils import embedding_utils
    import numpy as np

    # Patch the file opening to use our test file
    original_open = open

    def patched_open(file_path, *args, **kwargs):
        if "mock_data.json" in str(file_path):
            return original_open(sample_json_data, *args, **kwargs)
        return original_open(file_path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", patched_open)

    # Patch check_for_cached_embeddings to return no cache for tests
    def mock_check_for_cached_embeddings(data_path):
        return str(sample_json_data.parent / "embeddings_cache.pkl"), None

    monkeypatch.setattr(embedding_utils, "check_for_cached_embeddings", mock_check_for_cached_embeddings)

    # Patch get_image_embedding to return dummy embeddings
    def mock_get_image_embedding(model, processor, cached_embeddings, idx, image_url):
        # Return a dummy embedding array
        return np.array([0.1 * idx, 0.2 * idx, 0.3 * idx], dtype=np.float32)

    monkeypatch.setattr(embedding_utils, "get_image_embedding", mock_get_image_embedding)

    # Patch save_embeddings_cache to do nothing in tests
    def mock_save_embeddings_cache(embeddings, cache_path):
        pass

    monkeypatch.setattr(embedding_utils, "save_embeddings_cache", mock_save_embeddings_cache)


def test_db_get_all_sources():
    db = SpaceDB(lm=DummyLM())
    sources = db.get_all_sources()
    assert isinstance(sources, list)
    assert len(sources) == 2
    assert sources[0]["name"] == "Test Source 1"
    assert sources[1]["name"] == "Test Source 2"
    # Embedding key should not be present in get_all_sources
    assert EMBEDDING_KEY not in sources[0]
    assert EMBEDDING_KEY not in sources[1]


def test_db_get_all_sources_with_embedding():
    db = SpaceDB(lm=DummyLM())
    sources = db.get_all_sources_with_embedding()
    assert isinstance(sources, list)
    assert len(sources) == 2
    assert EMBEDDING_KEY in sources[0]
    assert EMBEDDING_KEY in sources[1]


def test_db_source_fields():
    db = SpaceDB(lm=DummyLM())
    sources = db.get_all_sources()
    for source in sources:
        assert {"id", "name", "type", "launch_date", "description", "image_url", "status"}.issubset(source.keys())
