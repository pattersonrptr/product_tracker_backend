import pytest
from datetime import time
from pydantic import ValidationError

from src.app.interfaces.schemas.search_config_schema import (
    SearchConfigBase,
    SearchConfigCreate,
    SearchConfigUpdate,
    SearchConfigInDBBase,
    SearchConfig,
    SearchConfigSearchResults,
    SearchConfigRead,
    SearchConfigsBulkDeleteRequest,
    PaginatedSearchConfigResponse,
)
from src.app.interfaces.schemas.source_website_schema import SourceWebsiteRead


def test_search_config_base_valid():
    data = {
        "search_term": "notebook",
        "is_active": True,
        "frequency_days": 2,
        "preferred_time": time(8, 30),
        "search_metadata": {"brand": "Dell"},
        "source_websites": [
            SourceWebsiteRead(
                id=1, name="OLX", base_url="https://olx.com.br", is_active=True
            )
        ],
        "user_id": 42,
    }
    obj = SearchConfigBase(**data)
    assert obj.search_term == "notebook"
    assert obj.frequency_days == 2
    assert obj.preferred_time == time(8, 30)
    assert obj.search_metadata == {"brand": "Dell"}
    assert obj.source_websites[0].id == 1
    assert obj.user_id == 42


def test_search_config_base_defaults():
    obj = SearchConfigBase(search_term="celular")
    assert obj.is_active is True
    assert obj.frequency_days == 1
    assert obj.preferred_time == time(0, 0)
    assert obj.search_metadata is None
    assert obj.source_websites is None
    assert obj.user_id is None


def test_search_config_base_missing_required():
    with pytest.raises(ValidationError):
        SearchConfigBase()


def test_search_config_create_accepts_ids():
    obj = SearchConfigCreate(search_term="tv", source_websites=[1, 2])
    assert obj.source_websites == [1, 2]


def test_search_config_update_accepts_ids():
    obj = SearchConfigUpdate(search_term="tv", source_websites=[3])
    assert obj.source_websites == [3]


def test_search_config_in_db_base():
    obj = SearchConfigInDBBase(search_term="geladeira", id=5)
    assert obj.id == 5
    assert obj.is_active is True


def test_search_config_orm_mode():
    class Dummy:
        def __init__(self):
            self.id = 10
            self.search_term = "carro"
            self.is_active = False
            self.frequency_days = 3
            self.preferred_time = time(12, 0)
            self.search_metadata = None
            self.source_websites = None
            self.user_id = 1

    dummy = Dummy()
    obj = SearchConfigInDBBase.from_orm(dummy)
    assert obj.id == 10
    assert obj.search_term == "carro"
    assert obj.is_active is False


def test_search_config_read():
    obj = SearchConfigRead(
        id=7,
        search_term="bicicleta",
        is_active=True,
        frequency_days=1,
        preferred_time=time(6, 0),
        search_metadata=None,
        source_websites=None,
        user_id=2,
    )
    assert obj.id == 7
    assert obj.search_term == "bicicleta"


def test_search_configs_bulk_delete_request():
    req = SearchConfigsBulkDeleteRequest(ids=[1, 2, 3])
    assert req.ids == [1, 2, 3]


def test_search_configs_bulk_delete_request_empty():
    with pytest.raises(ValidationError):
        SearchConfigsBulkDeleteRequest(ids=None)


def test_paginated_search_config_response():
    items = [
        SearchConfigRead(
            id=1,
            search_term="livro",
            is_active=True,
            frequency_days=1,
            preferred_time=time(0, 0),
            search_metadata=None,
            source_websites=None,
            user_id=1,
        )
    ]
    resp = PaginatedSearchConfigResponse(items=items, total_count=1, limit=10, offset=0)
    assert resp.total_count == 1
    assert resp.limit == 10
    assert resp.offset == 0
    assert len(resp.items) == 1


def test_search_config_search_results():
    configs = [
        SearchConfig(
            id=1,
            search_term="cadeira",
            is_active=True,
            frequency_days=1,
            preferred_time=time(0, 0),
            search_metadata=None,
            source_websites=None,
            user_id=1,
        )
    ]
    results = SearchConfigSearchResults(results=configs)
    assert len(results.results) == 1
    assert results.results[0].search_term == "cadeira"
