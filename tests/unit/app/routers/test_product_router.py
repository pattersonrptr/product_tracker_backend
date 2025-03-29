from datetime import datetime, UTC
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import pytest
from pydantic import HttpUrl
from sqlalchemy.orm.session import Session
from app.main import app
from app.repositories.product_repository import ProductRepository
from app.schemas.product_schema import (
    ProductResponse,
    ProductStats,
    ProductPartialResponse,
)
from app.services.product_service import ProductService


@pytest.fixture
def mock_product_service():
    return MagicMock()

@pytest.fixture
def client(mock_product_service):
    def override_get_product_service():
        return mock_product_service

    from app.routers.product_router import get_product_service

    app.dependency_overrides[get_product_service] = override_get_product_service
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_filter_products(client, mock_product_service):
    mock_product = ProductResponse(
        id=1,
        url="http://example.com",
        title="Test Product",
        price=10.0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_product_service.filter_products.return_value = [mock_product]

    response = client.get("/products/", params={"title": "Test"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Product"
    mock_product_service.filter_products.assert_called_once_with({"title": "Test"})

def test_get_product_exists(client, mock_product_service):
    mock_product = ProductResponse(
        id=1,
        url="http://example.com",
        title="Test Product",
        price=10.0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_product_service.get_product_by_id.return_value = mock_product

    response = client.get("/products/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    mock_product_service.get_product_by_id.assert_called_once_with(1)

def test_get_product_not_found(client, mock_product_service):
    mock_product_service.get_product_by_id.return_value = None

    response = client.get("/products/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

def test_search_products(client, mock_product_service):
    mock_product = ProductResponse(
        id=1,
        url="http://example.com",
        title="Test Product",
        price=10.0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_product_service.search_products.return_value = [mock_product]

    response = client.get("/products/search/", params={"query": "Test"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    mock_product_service.search_products.assert_called_once_with("Test")

def test_get_product_stats(client, mock_product_service):
    mock_stats = ProductStats(
        total_products=5,
        average_price=30.0,
        min_price=10.0,
        max_price=50.0,
    )
    mock_product_service.get_product_stats.return_value = mock_stats

    response = client.get("/products/stats/")
    assert response.status_code == 200
    data = response.json()
    assert data["total_products"] == 5
    assert data["average_price"] == 30.0

# Testes para GET /products/minimal/
def test_get_minimal_products(client, mock_product_service):
    mock_minimal = [
        ProductPartialResponse(id=1, title="Product 1", price=10.0),
        ProductPartialResponse(id=2, title="Product 2", price=20.0),
    ]
    mock_product_service.get_minimal_products.return_value = mock_minimal

    response = client.get("/products/minimal/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(
        "id" in item and "title" in item and "price" in item for item in data
    )


def test_create_product(client, mock_product_service):
    product_data = {
        "url": HttpUrl("http://example.com"),
        "title": "New Product",
        "price": 29.99,
    }

    mock_product = ProductResponse(
        id=1,
        url=product_data["url"],
        title=product_data["title"],
        price=product_data["price"],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_product_service.create_product.return_value = mock_product

    response = client.post("/products/", json={
        "url": str(product_data["url"]),
        "title": "New Product",
        "price": 29.99
    })

    assert response.status_code == 201
    assert response.json()["id"] == 1

    mock_product_service.create_product.assert_called_once_with({
        "url": HttpUrl("http://example.com"),
        "title": "New Product",
        "price": 29.99
    })

def test_create_product_invalid_data(client):
    invalid_data = {"url": "invalid", "title": "", "price": -5}
    response = client.post("/products/", json=invalid_data)
    assert response.status_code == 422

def test_bulk_create_products(client, mock_product_service):
    products_data = {
        "products": [
            {"url": "http://example.com/1", "title": "Product 1", "price": 10.0},
            {"url": "http://example.com/2", "title": "Product 2", "price": 20.0},
        ]
    }
    mock_products = [
        ProductResponse(
            id=i + 1,
            url=p["url"],
            title=p["title"],
            price=p["price"],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        for i, p in enumerate(products_data["products"])
    ]
    mock_product_service.create_product.side_effect = mock_products

    response = client.post("/products/bulk/", json=products_data)
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert mock_product_service.create_product.call_count == 2

def test_bulk_create_empty_list(client):
    invalid_data = {"products": []}
    response = client.post("/products/bulk/", json=invalid_data)
    assert response.status_code == 422

def test_update_product(client, mock_product_service):
    updated_data = {"title": "Updated Title"}
    mock_product = ProductResponse(
        id=1,
        url="http://example.com",
        title="Updated Title",
        price=10.0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_product_service.update_product.return_value = mock_product

    response = client.put("/products/1", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    mock_product_service.update_product.assert_called_once_with(1, updated_data)

def test_update_product_not_found(client, mock_product_service):
    mock_product_service.update_product.return_value = None

    response = client.put("/products/999", json={"title": "New Title"})
    assert response.status_code == 404

def test_delete_product(client, mock_product_service):
    mock_product_service.delete_product.return_value = True

    response = client.delete("/products/1")
    assert response.status_code == 204
    mock_product_service.delete_product.assert_called_once_with(1)

def test_delete_product_not_found(client, mock_product_service):
    mock_product_service.delete_product.return_value = False

    response = client.delete("/products/999")
    assert response.status_code == 404

def test_get_db_dependency():
    from app.routers.product_router import get_db
    generator = get_db()

    try:
        db = next(generator)
        assert db is not None
        assert isinstance(db, Session)
    finally:
        try:
            next(generator)
        except StopIteration:
            pass

def test_get_product_service_dependency():
    from app.routers.product_router import get_product_service
    from sqlalchemy.orm import Session

    mock_db = MagicMock(spec=Session)
    service = get_product_service(db=mock_db)

    assert isinstance(service, ProductService)
    assert isinstance(service.repository, ProductRepository)
    assert service.repository.db is mock_db
