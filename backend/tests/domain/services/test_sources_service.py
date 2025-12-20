import pytest

from app.domain.models import Source
from app.domain.services.sources_service import SourcesService
from tests.tests_utils import DummyDB


@pytest.fixture
def dummy_db():
    return DummyDB(include_embeddings=False)


def test_sources_service_get_all_sources(dummy_db):
    svc = SourcesService(db=dummy_db)
    result = svc.get_all_sources()
    assert isinstance(result, list)
    assert all(isinstance(r, Source) for r in result)
    # DummyDB now has 5 sources (updated for history tests)
    assert {r.id for r in result} == {1, 2, 3, 4, 5}
    assert result[0].name == "Apollo 11"
    assert result[1].name == "Voyager 1"


def test_sources_service_returns_empty_list_when_no_sources():
    class EmptyDB:
        def get_all_sources(self):
            return []

    svc = SourcesService(db=EmptyDB())
    result = svc.get_all_sources()
    assert isinstance(result, list)
    assert result == []
