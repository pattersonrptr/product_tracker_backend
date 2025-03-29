import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock
from app.routers.product_router import router, get_product_service
from app.schemas.product_schema import ProductResponse
from datetime import datetime
from pydantic import HttpUrl
from typing import cast, Dict, Callable


@pytest.fixture
def mock_product_service():
    return Mock()


@pytest.fixture
def client(mock_product_service):
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    def override_dependency():
        return mock_product_service

    app.dependency_overrides = cast(Dict[Callable, Callable], {})
    app.dependency_overrides[get_product_service] = override_dependency

    return TestClient(app)


def test_create_product_success(client, mock_product_service):
    input_data = {
        "url": "http://example.com",
        "title": "Test Product",
        "price": 100.0
    }

    expected_response = {
        "id": 1,
        "url": "http://example.com/",
        "title": "Test Product",
        "price": 100.0,
        "created_at": "2024-05-20T12:00:00",
        "updated_at": "2024-05-20T12:00:00"
    }

    mock_product_service.create_product = Mock(
        return_value=ProductResponse(
            id=1,
            url=HttpUrl("http://example.com"),
            title="Test Product",
            price=100.0,
            created_at=datetime.fromisoformat("2024-05-20T12:00:00"),
            updated_at=datetime.fromisoformat("2024-05-20T12:00:00"),
        )
    )

    response = client.post("/products/", json=input_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == expected_response

    mock_product_service.create_product.assert_called_once()


def test_filter_products_success(client, mock_product_service):
    mock_response = [
        ProductResponse(
            id=0,
            url=HttpUrl("https://example.com/"),
            title="string",
            price=1,
            created_at=datetime.fromisoformat("2024-05-20T12:00:00"),
            updated_at=datetime.fromisoformat("2024-05-20T12:00:00"),
        )
    ]

    expected_response = [
        {
            "url": "https://example.com/",
            "title": "string",
            "price": 1,
            "id": 0,
            "created_at": "2024-05-20T12:00:00",
            "updated_at": "2024-05-20T12:00:00",
        }
    ]

    mock_product_service.filter_products = Mock(return_value=mock_response)

    response = client.get("/products/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response
    mock_product_service.filter_products.assert_called_once_with({})

def test_get_product_success(client, mock_product_service):
    product_id = 1
    expected_response = {
        "id": 1,
        "url": "http://example.com/",
        "title": "Test Product",
        "price": 100.0,
        "created_at": "2024-05-20T12:00:00",
        "updated_at": "2024-05-20T12:00:00",
    }

    mock_product_service.get_product_by_id = Mock(
        return_value=ProductResponse(
            id=1,
            url=HttpUrl("http://example.com"),
            title="Test Product",
            price=100.0,
            created_at=datetime.fromisoformat("2024-05-20T12:00:00"),
            updated_at=datetime.fromisoformat("2024-05-20T12:00:00"),
        )
    )

    response = client.get(f"/products/{product_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response

    mock_product_service.get_product_by_id.assert_called_once_with(product_id)


def test_get_product_not_found(client, mock_product_service):
    product_id = 999

    mock_product_service.get_product_by_id = Mock(return_value=None)

    response = client.get(f"/products/{product_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Product not found"}

    mock_product_service.get_product_by_id.assert_called_once_with(product_id)


def test_update_product_success(client, mock_product_service):
    product_id = 1
    input_data = {
        "url": "http://updated.com",
        "title": "Updated Product",
        "price": 150.0
    }

    expected_response = {
        "id": 1,
        "url": "http://updated.com/",
        "title": "Updated Product",
        "price": 150.0,
        "created_at": "2024-05-20T12:00:00",
        "updated_at": "2024-05-20T12:00:00",
    }

    mock_product_service.update_product = Mock(
        return_value=ProductResponse(
            id=1,
            url=HttpUrl("http://updated.com/"),
            title="Updated Product",
            price=150.0,
            created_at=datetime.fromisoformat("2024-05-20T12:00:00"),
            updated_at=datetime.fromisoformat("2024-05-20T12:00:00"),
        )
    )

    response = client.put(f"/products/{product_id}", json=input_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response

    mock_product_service.update_product.assert_called_once_with(
        product_id,
        {
            "url": HttpUrl("http://updated.com/"),
            "title": "Updated Product",
            "price": 150.0
        }
    )


def test_update_product_not_found(client, mock_product_service):
    product_id = 999
    input_data = {
        "url": "http://updated.com",
        "title": "Updated Product",
        "price": 150.0
    }

    mock_product_service.update_product = Mock(return_value=None)

    response = client.put(f"/products/{product_id}", json=input_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Product not found"}

    mock_product_service.update_product.assert_called_once_with(
        product_id,
        {
            "url": HttpUrl("http://updated.com/"),
            "title": "Updated Product",
            "price": 150.0
        }
    )


def test_delete_product_success(client, mock_product_service):
    product_id = 1
    mock_product_service.delete_product = Mock(return_value=True)
    response = client.delete(f"/products/{product_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    mock_product_service.delete_product.assert_called_once_with(product_id)


def test_delete_product_not_found(client, mock_product_service):
    product_id = 999
    mock_product_service.delete_product = Mock(return_value=False)

    response = client.delete(f"/products/{product_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Product not found"}

    mock_product_service.delete_product.assert_called_once_with(product_id)
