from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from pydantic import HttpUrl

from app.main import app
from app.services.product_service import ProductService
from app.schemas.product_schema import ProductResponse


def test_product_router_included():
    routes = [route.path for route in app.routes]
    assert any(route.startswith("/products") for route in routes), "Route /products not found"


def test_product_endpoint():
    mock_data = [
        ProductResponse(
            id=1,
            url=HttpUrl("https://example.com/product1"),
            title="Product X",
            price=99.99,
            created_at=datetime(2024, 5, 20, 10, 30),
        ),
        ProductResponse(
            id=2,
            url=HttpUrl("https://example.com/product2"),
            title="Product Y",
            price=149.99,
            created_at=datetime(2024, 5, 20, 11, 0),
        )
    ]

    mock_service = AsyncMock(spec=ProductService)
    mock_service.get_all_products = AsyncMock(return_value=mock_data)

    from app.routers.product_router import get_product_service
    app.dependency_overrides[get_product_service] = lambda: mock_service

    client = TestClient(app)

    try:
        response = client.get("/products/")
        assert response.status_code == 200

        assert response.json() == [
            {
                "id": 1,
                "url": "https://example.com/product1",
                "title": "Product X",
                "price": 99.99,
                "created_at": "2024-05-20T10:30:00"
            },
            {
                "id": 2,
                "url": "https://example.com/product2",
                "title": "Product Y",
                "price": 149.99,
                "created_at": "2024-05-20T11:00:00"
            }
        ]
    finally:
        app.dependency_overrides.clear()


def test_docs_endpoint():
    client = TestClient(app)

    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/redoc")
    assert response.status_code == 200


def test_nonexistent_route():
    client = TestClient(app)

    response = client.get("/nonexistent-route")
    assert response.status_code == 404
