import pytest
from datetime import datetime

from src.app.interfaces.schemas.product_schema import (
    ProductBase, ProductCreate, ProductRead, ProductUpdate,
    ProductMinimal, ProductsBulkDeleteRequest, PaginatedProductResponse
)
from src.app.infrastructure.database.models.product_model import ProductCondition

def test_product_base_minimal():
    obj = ProductBase(
        url="http://example.com",
        title="Produto",
        city="Cidade",
        state="Estado",
        source_website_id=1
    )
    assert obj.url == "http://example.com"
    assert obj.condition == ProductCondition.USED

def test_product_create():
    obj = ProductCreate(
        url="http://example.com",
        title="Produto",
        city="Cidade",
        state="Estado",
        source_website_id=1,
        price=100.0
    )
    assert obj.price == 100.0

def test_product_read():
    now = datetime.utcnow()
    obj = ProductRead(
        id=1,
        url="http://example.com",
        title="Produto",
        city="Cidade",
        state="Estado",
        source_website_id=1,
        created_at=now,
        updated_at=now
    )
    assert obj.id == 1
    assert obj.created_at == now

def test_product_update():
    obj = ProductUpdate(
        url="http://example.com",
        title="Produto",
        city="Cidade",
        state="Estado",
        source_website_id=1,
        price=200.0
    )
    assert obj.price == 200.0

def test_product_minimal():
    obj = ProductMinimal(
        id=1,
        title="Produto",
        url="http://example.com",
        current_price=99.9
    )
    assert obj.current_price == 99.9

def test_products_bulk_delete_request():
    req = ProductsBulkDeleteRequest(ids=[1, 2, 3])
    assert req.ids == [1, 2, 3]

def test_paginated_product_response():
    now = datetime.utcnow()
    items = [
        ProductRead(
            id=1,
            url="http://example.com",
            title="Produto",
            city="Cidade",
            state="Estado",
            source_website_id=1,
            created_at=now,
            updated_at=now
        )
    ]
    resp = PaginatedProductResponse(items=items, total_count=1, limit=10, offset=0)
    assert resp.total_count == 1
    assert resp.limit == 10
    assert resp.offset == 0
    assert len(resp.items) == 1
