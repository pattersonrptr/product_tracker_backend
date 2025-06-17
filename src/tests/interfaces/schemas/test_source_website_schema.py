import pytest
from pydantic import ValidationError
from src.app.interfaces.schemas.source_website_schema import (
    SourceWebsiteBase,
    SourceWebsiteCreate,
    SourceWebsiteRead,
    SourceWebsiteUpdate,
    SourceWebsitesBulkDeleteRequest,
    PaginatedSourceWebsiteResponse,
)

def test_source_website_base_valid():
    data = {
        "name": "OLX",
        "base_url": "https://olx.com.br",
        "is_active": True,
    }
    obj = SourceWebsiteBase(**data)
    assert obj.name == "OLX"
    assert obj.base_url == "https://olx.com.br"
    assert obj.is_active is True

def test_source_website_base_missing_fields():
    with pytest.raises(ValidationError):
        SourceWebsiteBase()

def test_source_website_create():
    data = {"name": "Enjoei", "base_url": "https://enjoei.com.br"}
    obj = SourceWebsiteCreate(**data)
    assert obj.name == "Enjoei"
    assert obj.base_url == "https://enjoei.com.br"
    assert obj.is_active is True

def test_source_website_read():
    data = {"id": 1, "name": "OLX", "base_url": "https://olx.com.br", "is_active": False}
    obj = SourceWebsiteRead(**data)
    assert obj.id == 1
    assert obj.is_active is False

def test_source_website_update():
    data = {"name": "OLX", "base_url": "https://olx.com.br", "is_active": True}
    obj = SourceWebsiteUpdate(**data)
    assert obj.name == "OLX"
    assert obj.is_active is True

def test_bulk_delete_request():
    data = {"ids": [1, 2, 3]}
    obj = SourceWebsitesBulkDeleteRequest(**data)
    assert obj.ids == [1, 2, 3]

def test_bulk_delete_request_empty():
    with pytest.raises(ValidationError):
        SourceWebsitesBulkDeleteRequest(ids=None)

def test_paginated_source_website_response():
    items = [SourceWebsiteRead(id=1, name="OLX", base_url="https://olx.com.br", is_active=True)]
    resp = PaginatedSourceWebsiteResponse(items=items, total_count=1, limit=10, offset=0)
    assert resp.total_count == 1
    assert resp.limit == 10
    assert resp.offset == 0
    assert len(resp.items) == 1
