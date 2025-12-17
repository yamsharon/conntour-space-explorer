from unittest.mock import MagicMock

import pytest
import torch

from app.domain.models import SearchResult, Source
from app.domain.services import search_service
from app.domain.services.search_service import (
    SearchService,
    normalize_results,
    calculate_similarity_for_one_source,
)


@pytest.fixture
def mock_db():
    mock_db = MagicMock()
    mock_db.get_all_sources_with_embedding.return_value = [
        {
            "id": "1",
            "name": "Apollo 11",
            "type": "Mission",
            "launch_date": "1969-07-16",
            "description": "First Moon landing.",
            "image_url": "https://example.com/apollo11.jpg",
            "status": "Complete",
            "embedding": [0.2, 0.5, 0.7]
        },
        {
            "id": "2",
            "name": "Voyager 1",
            "type": "Probe",
            "launch_date": "1977-09-05",
            "description": "Farthest spacecraft from Earth.",
            "image_url": "https://example.com/voyager1.jpg",
            "status": "Active",
            "embedding": [0.9, 0.3, 0.4]
        }
    ]
    return mock_db


@pytest.fixture
def mock_lm():
    mock_lm = MagicMock()
    mock_lm.processor.return_value = {"input_ids": torch.zeros((1, 3), dtype=torch.int64)}
    mock_model = MagicMock()
    # get_text_features should return a tensor for further usage in search
    mock_model.get_text_features.return_value = torch.tensor([[0.1, 0.2, 0.3]])
    mock_lm.model = mock_model
    return mock_lm


def test_normalize_results_typical_case():
    results = [
        SearchResult(id="1", name="A", type="Type", launch_date="x", description="a", image_url="url", status="done",
                     confidence=30.0),
        SearchResult(id="2", name="B", type="Type", launch_date="x", description="b", image_url="url", status="done",
                     confidence=80.0),
        SearchResult(id="3", name="C", type="Type", launch_date="x", description="c", image_url="url", status="done",
                     confidence=50.0),
    ]
    norm = normalize_results(results)
    scores = [r.confidence for r in norm]
    assert min(scores) >= 0.2 and max(scores) <= 1.0
    assert norm[0].confidence < norm[1].confidence


def test_normalize_results_all_same_score():
    results = [
        SearchResult(id="1", name="A", type="Type", launch_date="x", description="a", image_url="url", status="done",
                     confidence=50.0),
        SearchResult(id="2", name="B", type="Type", launch_date="x", description="b", image_url="url", status="done",
                     confidence=50.0)
    ]
    norm = normalize_results(results)
    for r in norm:
        assert r.confidence == 0.6


def test_calculate_similarity_for_one_source_returns_search_result(monkeypatch):
    dummy_embedding = [1.0, 2.0, 3.0]
    source_dict = {
        "id": "1",
        "name": "Apollo",
        "type": "Mission",
        "launch_date": "1969-07-16",
        "description": "Test",
        "image_url": "url",
        "status": "Active",
        "embedding": dummy_embedding
    }
    text_vec = torch.tensor([[1.0, 2.0, 3.0]])

    # Patch EMBEDDING_KEY used in the function
    monkeypatch.setattr(search_service, 'EMBEDDING_KEY', "embedding")
    # Patch the similarity function to return a fixed value
    monkeypatch.setattr(search_service, 'calculate_image_and_text_similarity', lambda img, txt: 0.8)

    result = calculate_similarity_for_one_source(source_dict, text_vec)
    assert isinstance(result, SearchResult)
    assert result.confidence == 80.0
    assert result.name == "Apollo"


def test_search_service_search_returns_normalized_results_sorted(mock_db, mock_lm, monkeypatch):
    # Patch EMBEDDING_KEY used in search_service
    monkeypatch.setattr(search_service, 'EMBEDDING_KEY', "embedding")
    # Patch calculate_image_and_text_similarity to make the results deterministic
    similarity_scores = [0.9, 0.1]

    def fake_similarity(img, txt):
        # For this test we just pop one for each call
        return similarity_scores.pop(0)

    monkeypatch.setattr(search_service, 'calculate_image_and_text_similarity', fake_similarity)

    svc = SearchService(db=mock_db, lm=mock_lm)
    results = svc.search("moon mission", limit=2)
    assert isinstance(results, list)
    assert len(results) == 2
    # Scores should be 90.0, 10.0, then normalized to [0.2, 1.0]
    assert results[0].confidence > results[1].confidence
    assert all(0.2 <= r.confidence <= 1.0 for r in results)
    # Names should correspond to mock data
    assert results[0].name in ["Apollo 11", "Voyager 1"]


def test_search_service_search_empty_query_returns_empty_list(mock_db, mock_lm):
    svc = SearchService(db=mock_db, lm=mock_lm)
    results = svc.search("   ")
    assert results == []
