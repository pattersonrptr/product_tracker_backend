import pytest
from unittest.mock import AsyncMock, create_autospec
from app.services.product_service import ProductService
from app.repositories.product_repository import ProductRepository

@pytest.fixture
def mock_repository():
    repo = create_autospec(ProductRepository, instance=True)
    for method in ['create', 'get_all', 'get_by_id', 'update', 'delete']:
        setattr(repo, method, AsyncMock())
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
async def test_get_all_products_success(product_service, mock_repository):
    # Dados de teste
    expected_result = [
        {"id": 1, "name": "Product X", "price": 99.99},
        {"id": 2, "name": "Product Y", "price": 149.99}
    ]

    mock_repository.get_all = AsyncMock(return_value=expected_result)
    result = await product_service.get_all_products()

    mock_repository.get_all.assert_awaited_once()
    assert result == expected_result

@pytest.mark.asyncio
async def test_get_all_products_empty(product_service, mock_repository):
    mock_repository.get_all = AsyncMock(return_value=[])
    result = await product_service.get_all_products()
    assert result == []

@pytest.mark.asyncio
async def test_get_product_by_id_success(product_service, mock_repository):
    product_id = 1
    expected_result = {"id": 1, "name": "Product X", "price": 99.99}
    mock_repository.get_by_id = AsyncMock(return_value=expected_result)
    result = await product_service.get_product_by_id(product_id)

    mock_repository.get_by_id.assert_awaited_once_with(product_id)
    assert result == expected_result

@pytest.mark.asyncio
async def test_get_product_by_id_not_found(product_service, mock_repository):
    product_id = 999
    mock_repository.get_by_id = AsyncMock(return_value=None)
    result = await product_service.get_product_by_id(product_id)

    mock_repository.get_by_id.assert_awaited_once_with(product_id)
    assert result is None

@pytest.mark.asyncio
async def test_update_product_success(product_service, mock_repository):
    product_id = 1
    update_data = {"name": "Product X Updated", "price": 129.99}
    expected_result = {"id": product_id, **update_data}
    mock_repository.update = AsyncMock(return_value=expected_result)
    result = await product_service.update_product(product_id, update_data)

    mock_repository.update.assert_awaited_once_with(product_id, update_data)
    assert result == expected_result

@pytest.mark.asyncio
async def test_update_product_not_found(product_service, mock_repository):
    product_id = 999
    update_data = {"name": "Non-existent Product"}

    mock_repository.update = AsyncMock(return_value=None)
    result = await product_service.update_product(product_id, update_data)

    mock_repository.update.assert_awaited_once_with(product_id, update_data)
    assert result is None

@pytest.mark.asyncio
async def test_delete_product_success(product_service, mock_repository):
    product_id = 1
    expected_result = True
    mock_repository.delete = AsyncMock(return_value=expected_result)
    result = await product_service.delete_product(product_id)

    mock_repository.delete.assert_awaited_once_with(product_id)
    assert result is True

@pytest.mark.asyncio
async def test_delete_product_not_found(product_service, mock_repository):
    product_id = 999
    mock_repository.delete = AsyncMock(return_value=False)
    result = await product_service.delete_product(product_id)

    mock_repository.delete.assert_awaited_once_with(product_id)
    assert result is False
