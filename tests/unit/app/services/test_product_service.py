import pytest
from unittest.mock import patch
from datetime import datetime, UTC, timedelta
from pydantic import HttpUrl
from app.services.product_service import ProductService
from app.repositories.product_repository import ProductRepository



# Fixtures
from unittest.mock import Mock, AsyncMock, create_autospec


@pytest.fixture
def mock_repository():
    repo = create_autospec(ProductRepository, instance=True)

    for method in ['create', 'get_all', 'get_by_id', 'get_products_older_than', 'update', 'update_by_url', 'delete']:
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

    mock_repository.create.assert_awaited_once_with({"url": str(url), "name": "Product X", "price": 99.99})
    assert result == expected_result

@pytest.mark.asyncio
async def test_get_all_products_success(product_service, mock_repository):
    expected_result = [
        {"id": 1, "name": "Product X", "price": 99.99},
        {"id": 2, "name": "Product Y", "price": 149.99}
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
async def test_get_products_older_than(product_service, mock_repository):
    days = 7
    current_date = datetime(2025, 3, 16, 4, 15, 11, 533458, tzinfo=UTC)
    cutoff_date = current_date - timedelta(days=days)  # Subtrai os dias

    expected_result = [
        {"id": 1, "name": "Product X", "price": 99.99, "updated_at": cutoff_date - timedelta(days=1)}
    ]

    mock_repository.get_products_older_than.return_value = expected_result

    with patch("app.services.product_service.datetime") as mock_datetime:
        mock_datetime.now.return_value = current_date
        result = await product_service.get_products_older_than(days)

        mock_repository.get_products_older_than.assert_awaited_once_with(cutoff_date)

    assert result == expected_result


@pytest.mark.asyncio
async def test_get_products_older_than_empty(product_service, mock_repository):
    days = 7
    mock_repository.get_products_older_than.return_value = []
    result = await product_service.get_products_older_than(days)
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

    mock_repository.update.assert_awaited_once_with(product_id, {"url": str(url), "name": "Updated Product"})
    assert result == expected_result

@pytest.mark.asyncio
async def test_update_product_by_url_with_http_url(product_service, mock_repository):
    url = "https://example.com"
    new_url = HttpUrl("https://updated.com")
    update_data = {"url": new_url, "name": "Updated Product"}
    expected_result = {"url": str(new_url), "name": "Updated Product"}

    mock_repository.update_by_url.return_value = expected_result
    result = await product_service.update_product_by_url(url, update_data)

    mock_repository.update_by_url.assert_awaited_once_with(url, {"url": str(new_url), "name": "Updated Product"})
    assert result == expected_result

@pytest.mark.asyncio
async def test_update_product_by_url_without_http_url(product_service, mock_repository):
    url = "https://example.com"
    update_data = {"name": "Updated Product"}
    expected_result = {"url": url, "name": "Updated Product"}

    mock_repository.update_by_url.return_value = expected_result
    result = await product_service.update_product_by_url(url, update_data)

    mock_repository.update_by_url.assert_awaited_once_with(url, {"name": "Updated Product"})
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