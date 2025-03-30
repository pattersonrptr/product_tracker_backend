from unittest.mock import AsyncMock, Mock, create_autospec

import pytest
from pydantic import HttpUrl

from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService


@pytest.fixture
def mock_repository():
    repo = create_autospec(ProductRepository, instance=True)

    for method in [
        "create",
        "get_all",
        "get_by_id",
        "get_products_older_than",
        "update",
        "update_by_url",
        "delete",
        "filter_products",
        "search_products",
        "get_product_stats",
        "get_minimal_products",
    ]:
        setattr(repo, method, AsyncMock())

    repo.get_by_url = Mock()
    return repo


@pytest.fixture
def product_service(mock_repository):
    return ProductService(mock_repository)


@pytest.mark.asyncio
async def test_create_product_success(product_service, mock_repository):
    test_data = {"name": "Product X", "price": 99.99}
    expected_result = {"id": 1, **test_data}
    mock_repository.create.return_value = expected_result
    result = await product_service.create_product(test_data)

    mock_repository.create.assert_awaited_once_with(test_data)
    assert result == expected_result


@pytest.mark.asyncio
async def test_create_product_database_error(product_service, mock_repository):
    mock_repository.create.side_effect = Exception("DB error")
    with pytest.raises(Exception, match="DB error"):
        await product_service.create_product({"name": "Product X"})


@pytest.mark.asyncio
async def test_create_product_with_http_url(product_service, mock_repository):
    url = HttpUrl("https://example.com")
    test_data = {"url": url, "name": "Product X", "price": 99.99}
    expected_result = {"id": 1, "url": str(url), "name": "Product X", "price": 99.99}

    mock_repository.create.return_value = expected_result
    result = await product_service.create_product(test_data)

    mock_repository.create.assert_awaited_once_with(
        {"url": str(url), "name": "Product X", "price": 99.99}
    )
    assert result == expected_result


@pytest.mark.asyncio
async def test_filter_products(product_service, mock_repository):
    filter_data = {"min_price": 100}
    expected_result = [{"id": 2, "name": "Product Y", "price": 149.99}]

    mock_repository.filter_products.return_value = expected_result
    result = await product_service.filter_products(filter_data)

    mock_repository.filter_products.assert_awaited_once_with(filter_data)
    assert result == expected_result


@pytest.mark.asyncio
async def test_search_products(product_service, mock_repository):
    query = "Product X"
    expected_result = [{"id": 1, "name": "Product X", "price": 99.99}]

    mock_repository.search_products.return_value = expected_result
    result = await product_service.search_products(query)

    mock_repository.search_products.assert_awaited_once_with(query)
    assert result == expected_result


@pytest.mark.asyncio
async def test_get_product_stats(product_service, mock_repository):
    expected_result = {"count": 2, "avg_price": 124.99}

    mock_repository.get_product_stats.return_value = expected_result
    result = await product_service.get_product_stats()

    mock_repository.get_product_stats.assert_awaited_once()
    assert result == expected_result


@pytest.mark.asyncio
async def test_get_minimal_products(product_service, mock_repository):
    expected_result = [{"id": 1, "name": "Product X"}, {"id": 2, "name": "Product Y"}]

    mock_repository.get_minimal_products.return_value = expected_result
    result = await product_service.get_minimal_products()

    mock_repository.get_minimal_products.assert_awaited_once()
    assert result == expected_result


@pytest.mark.asyncio
async def test_get_all_products_success(product_service, mock_repository):
    expected_result = [
        {"id": 1, "name": "Product X", "price": 99.99},
        {"id": 2, "name": "Product Y", "price": 149.99},
    ]

    mock_repository.get_all.return_value = expected_result
    result = await product_service.get_all_products()

    mock_repository.get_all.assert_awaited_once()
    assert result == expected_result


@pytest.mark.asyncio
async def test_get_all_products_empty(product_service, mock_repository):
    mock_repository.get_all.return_value = []
    result = await product_service.get_all_products()
    assert result == []


@pytest.mark.asyncio
async def test_get_product_by_id_success(product_service, mock_repository):
    product_id = 1
    expected_result = {"id": 1, "name": "Product X", "price": 99.99}
    mock_repository.get_by_id.return_value = expected_result
    result = await product_service.get_product_by_id(product_id)

    mock_repository.get_by_id.assert_awaited_once_with(product_id)
    assert result == expected_result


@pytest.mark.asyncio
async def test_get_product_by_id_not_found(product_service, mock_repository):
    product_id = 999
    mock_repository.get_by_id.return_value = None
    result = await product_service.get_product_by_id(product_id)

    mock_repository.get_by_id.assert_awaited_once_with(product_id)
    assert result is None


@pytest.mark.asyncio
async def test_get_product_by_url_found(product_service, mock_repository):
    url = "https://example.com"
    expected_result = {"id": 1, "url": url, "name": "Product X", "price": 99.99}
    mock_repository.get_by_url.return_value = expected_result
    result = product_service.get_product_by_url(url)
    mock_repository.get_by_url.assert_called_once_with(url)

    assert result == expected_result


@pytest.mark.asyncio
async def test_get_product_by_url_not_found(product_service, mock_repository):
    url = "https://nonexistent.com"
    mock_repository.get_by_url.return_value = None
    result = product_service.get_product_by_url(url)
    mock_repository.get_by_url.assert_called_once_with(url)

    assert result == []


@pytest.mark.asyncio
async def test_update_product_success(product_service, mock_repository):
    product_id = 1
    update_data = {"name": "Product X Updated", "price": 129.99}
    expected_result = {"id": product_id, **update_data}
    mock_repository.update.return_value = expected_result
    result = await product_service.update_product(product_id, update_data)

    mock_repository.update.assert_awaited_once_with(product_id, update_data)
    assert result == expected_result


@pytest.mark.asyncio
async def test_update_product_not_found(product_service, mock_repository):
    product_id = 999
    update_data = {"name": "Non-existent Product"}

    mock_repository.update.return_value = None
    result = await product_service.update_product(product_id, update_data)

    mock_repository.update.assert_awaited_once_with(product_id, update_data)
    assert result is None


@pytest.mark.asyncio
async def test_update_product_with_http_url(product_service, mock_repository):
    product_id = 1
    url = HttpUrl("https://updated.com")
    update_data = {"url": url, "name": "Updated Product"}
    expected_result = {"id": product_id, "url": str(url), "name": "Updated Product"}

    mock_repository.update.return_value = expected_result
    result = await product_service.update_product(product_id, update_data)

    mock_repository.update.assert_awaited_once_with(
        product_id, {"url": str(url), "name": "Updated Product"}
    )
    assert result == expected_result


@pytest.mark.asyncio
async def test_delete_product_success(product_service, mock_repository):
    product_id = 1
    mock_repository.delete.return_value = True
    result = await product_service.delete_product(product_id)

    mock_repository.delete.assert_awaited_once_with(product_id)
    assert result is True


@pytest.mark.asyncio
async def test_delete_product_not_found(product_service, mock_repository):
    product_id = 999
    mock_repository.delete.return_value = False
    result = await product_service.delete_product(product_id)

    mock_repository.delete.assert_awaited_once_with(product_id)
    assert result is False
