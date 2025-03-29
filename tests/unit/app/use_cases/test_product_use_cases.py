import pytest
from unittest.mock import AsyncMock, create_autospec
from app.use_cases.product_use_cases import (
    CreateProduct,
    DeleteProduct,
    GetProductById,
    UpdateProduct, FilterProducts, SearchProducts, GetProductStats, GetMinimalProducts,
)
from app.services.product_service import ProductService


@pytest.fixture
def mock_product_service():
    service = create_autospec(ProductService, instance=True)
    service.create_product = AsyncMock()
    service.delete_product = AsyncMock()
    service.get_products_older_than = AsyncMock()
    service.get_product_by_id = AsyncMock()
    service.get_product_by_url = AsyncMock()
    service.get_all_products = AsyncMock()
    service.update_product = AsyncMock()
    service.update_product_by_url = AsyncMock()
    service.filter_products = AsyncMock()
    service.search_products = AsyncMock()
    service.get_product_stats = AsyncMock()
    service.get_minimal_products = AsyncMock()
    return service

@pytest.fixture
def create_product_uc(mock_product_service):
    return CreateProduct(mock_product_service)

@pytest.fixture
def filter_products_uc(mock_product_service):
    return FilterProducts(mock_product_service)

@pytest.fixture
def search_products_uc(mock_product_service):
    return SearchProducts(mock_product_service)

@pytest.fixture
def get_product_stats_uc(mock_product_service):
    return GetProductStats(mock_product_service)

@pytest.fixture
def get_minimal_products_uc(mock_product_service):
    return GetMinimalProducts(mock_product_service)

@pytest.fixture
def delete_product_uc(mock_product_service):
    return DeleteProduct(mock_product_service)

@pytest.fixture
def get_product_by_id_uc(mock_product_service):
    return GetProductById(mock_product_service)

@pytest.fixture
def update_product_uc(mock_product_service):
    return UpdateProduct(mock_product_service)

@pytest.mark.asyncio
async def test_create_product_execute_success(create_product_uc, mock_product_service):
    test_data = {"name": "New Product", "price": 199.90}
    expected_result = {"id": 1, **test_data}
    mock_product_service.create_product.return_value = expected_result
    result = await create_product_uc.execute(test_data)

    mock_product_service.create_product.assert_awaited_once_with(test_data)
    assert result == expected_result

@pytest.mark.asyncio
async def test_create_product_execute_propagates_errors(create_product_uc, mock_product_service):
    error = Exception("Database error")
    mock_product_service.create_product.side_effect = error

    with pytest.raises(Exception) as exc_info:
        await create_product_uc.execute({"name": "Invalid"})

    assert exc_info.value is error

@pytest.mark.asyncio
async def test_delete_product_execute_success(delete_product_uc, mock_product_service):
    product_id = 1
    mock_product_service.delete_product.return_value = True
    result = await delete_product_uc.execute(product_id)

    mock_product_service.delete_product.assert_awaited_once_with(product_id)
    assert result is True

@pytest.mark.asyncio
async def test_get_product_by_id_execute_success(get_product_by_id_uc, mock_product_service):
    product_id = 1
    expected_result = {"id": 1, "name": "Product 1"}
    mock_product_service.get_product_by_id.return_value = expected_result
    result = await get_product_by_id_uc.execute(product_id)

    mock_product_service.get_product_by_id.assert_awaited_once_with(product_id)
    assert result == expected_result

@pytest.mark.asyncio
async def test_update_product_execute_success(update_product_uc, mock_product_service):
    product_id = 1
    product_data = {"name": "Updated Product"}
    expected_result = {"id": 1, **product_data}
    mock_product_service.update_product.return_value = expected_result
    result = await update_product_uc.execute(product_id, product_data)

    mock_product_service.update_product.assert_awaited_once_with(product_id, product_data)
    assert result == expected_result


@pytest.mark.asyncio
async def test_filter_products_execute_success(filter_products_uc, mock_product_service):
    filter_data = {"min_price": 100}
    expected_result = [{"id": 2, "name": "Premium Product", "price": 199.99}]

    mock_product_service.filter_products.return_value = expected_result
    result = await filter_products_uc.execute(filter_data)

    mock_product_service.filter_products.assert_awaited_once_with(filter_data)
    assert result == expected_result


@pytest.mark.asyncio
async def test_search_products_execute_success(search_products_uc, mock_product_service):
    query = "special"
    expected_result = [{"id": 3, "name": "Special Edition", "price": 299.99}]

    mock_product_service.search_products.return_value = expected_result
    result = await search_products_uc.execute(query)

    mock_product_service.search_products.assert_awaited_once_with(query)
    assert result == expected_result


@pytest.mark.asyncio
async def test_get_product_stats_execute_success(get_product_stats_uc, mock_product_service):
    expected_result = {"total": 5, "average_price": 199.99}

    mock_product_service.get_product_stats.return_value = expected_result
    result = await get_product_stats_uc.execute()

    mock_product_service.get_product_stats.assert_awaited_once()
    assert result == expected_result


@pytest.mark.asyncio
async def test_get_minimal_products_execute_success(get_minimal_products_uc, mock_product_service):
    expected_result = [
        {"id": 1, "name": "Basic Product"},
        {"id": 2, "name": "Premium Product"}
    ]

    mock_product_service.get_minimal_products.return_value = expected_result
    result = await get_minimal_products_uc.execute()

    mock_product_service.get_minimal_products.assert_awaited_once()
    assert result == expected_result
