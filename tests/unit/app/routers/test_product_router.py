import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.routers.product_router import router, get_product_service
from app.schemas.product_schema import ProductResponse
from datetime import datetime
from pydantic import HttpUrl
from typing import cast, Dict, Callable


@pytest.fixture
def mock_product_service():
    return AsyncMock()


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


@pytest.mark.asyncio
async def test_create_product_success(client, mock_product_service):
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
        "created_at": "2024-05-20T12:00:00"
    }

    mock_product_service.create_product = AsyncMock(
        return_value=ProductResponse(
            id=1,
            url=HttpUrl("http://example.com"),
            title="Test Product",
            price=100.0,
            created_at=datetime.fromisoformat("2024-05-20T12:00:00")
        )
    )

    response = client.post("/products/", json=input_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == expected_response

    mock_product_service.create_product.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_products_success(client, mock_product_service):
    expected_response = [
        {
            "id": 1,
            "url": "http://example.com/",
            "title": "Test Product 1",
            "price": 100.0,
            "created_at": "2024-05-20T12:00:00"
        },
        {
            "id": 2,
            "url": "http://example2.com/",
            "title": "Test Product 2",
            "price": 200.0,
            "created_at": "2024-05-20T13:00:00"
        }
    ]

    mock_product_service.get_all_products = AsyncMock(
        return_value=[
            ProductResponse(
                id=1,
                url=HttpUrl("http://example.com"),
                title="Test Product 1",
                price=100.0,
                created_at=datetime.fromisoformat("2024-05-20T12:00:00")
            ),
            ProductResponse(
                id=2,
                url=HttpUrl("http://example2.com"),
                title="Test Product 2",
                price=200.0,
                created_at=datetime.fromisoformat("2024-05-20T13:00:00")
            )
        ]
    )

    response = client.get("/products/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response

    mock_product_service.get_all_products.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_product_success(client, mock_product_service):
    product_id = 1
    expected_response = {
        "id": 1,
        "url": "http://example.com/",
        "title": "Test Product",
        "price": 100.0,
        "created_at": "2024-05-20T12:00:00"
    }

    mock_product_service.get_product_by_id = AsyncMock(
        return_value=ProductResponse(
            id=1,
            url=HttpUrl("http://example.com"),
            title="Test Product",
            price=100.0,
            created_at=datetime.fromisoformat("2024-05-20T12:00:00")
        )
    )

    response = client.get(f"/products/{product_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response

    mock_product_service.get_product_by_id.assert_awaited_once_with(product_id)


@pytest.mark.asyncio
async def test_get_product_not_found(client, mock_product_service):
    product_id = 999

    mock_product_service.get_product_by_id = AsyncMock(return_value=None)

    response = client.get(f"/products/{product_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Product not found"}

    mock_product_service.get_product_by_id.assert_awaited_once_with(product_id)


@pytest.mark.asyncio
async def test_update_product_success(client, mock_product_service):
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
        "created_at": "2024-05-20T12:00:00"
    }

    mock_product_service.update_product = AsyncMock(
        return_value=ProductResponse(
            id=1,
            url=HttpUrl("http://updated.com/"),
            title="Updated Product",
            price=150.0,
            created_at=datetime.fromisoformat("2024-05-20T12:00:00")
        )
    )

    response = client.put(f"/products/{product_id}", json=input_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response

    mock_product_service.update_product.assert_awaited_once_with(
        product_id,
        {
            "url": HttpUrl("http://updated.com/"),
            "title": "Updated Product",
            "price": 150.0
        }
    )


@pytest.mark.asyncio
async def test_update_product_not_found(client, mock_product_service):
    product_id = 999
    input_data = {
        "url": "http://updated.com",
        "title": "Updated Product",
        "price": 150.0
    }

    mock_product_service.update_product = AsyncMock(return_value=None)

    response = client.put(f"/products/{product_id}", json=input_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Product not found"}

    mock_product_service.update_product.assert_awaited_once_with(
        product_id,
        {
            "url": HttpUrl("http://updated.com/"),
            "title": "Updated Product",
            "price": 150.0
        }
    )


@pytest.mark.asyncio
async def test_delete_product_success(client, mock_product_service):
    product_id = 1
    mock_product_service.delete_product = AsyncMock(return_value=True)
    response = client.delete(f"/products/{product_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    mock_product_service.delete_product.assert_awaited_once_with(product_id)


@pytest.mark.asyncio
async def test_delete_product_not_found(client, mock_product_service):
    product_id = 999
    mock_product_service.delete_product = AsyncMock(return_value=False)

    response = client.delete(f"/products/{product_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Product not found"}

    mock_product_service.delete_product.assert_awaited_once_with(product_id)
