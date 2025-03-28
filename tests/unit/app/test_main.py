from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import HttpUrl

from app.main import app
from app.services.product_service import ProductService
from app.schemas.product_schema import ProductResponse
from app.use_cases.product_use_cases import FilterProducts


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
            updated_at=datetime(2024, 5, 20, 10, 30),
        ),
        ProductResponse(
            id=2,
            url=HttpUrl("https://example.com/product2"),
            title="Product Y",
            price=149.99,
            created_at=datetime(2024, 5, 20, 11, 0),
            updated_at=datetime(2024, 5, 20, 11, 0),
        )
    ]

    mock_filter_use_case = MagicMock(spec=FilterProducts)
    mock_filter_use_case.execute.return_value = mock_data

    with patch('app.routers.product_router.FilterProducts', return_value=mock_filter_use_case):
        client = TestClient(app)

        response = client.get("/products/", params={})

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": 1,
                "url": "https://example.com/product1",
                "title": "Product X",
                "price": 99.99,
                "created_at": "2024-05-20T10:30:00",
                "updated_at": "2024-05-20T10:30:00",
            },
            {
                "id": 2,
                "url": "https://example.com/product2",
                "title": "Product Y",
                "price": 149.99,
                "created_at": "2024-05-20T11:00:00",
                "updated_at": "2024-05-20T11:00:00",
            }
        ]

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
