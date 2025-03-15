import pytest
from unittest.mock import AsyncMock, create_autospec
from app.use_cases.create_product import CreateProduct
from app.services.product_service import ProductService


@pytest.fixture
def mock_product_service():
    service = create_autospec(ProductService, instance=True)
    service.create_product = AsyncMock()
    return service


@pytest.fixture
def create_product_uc(mock_product_service):
    return CreateProduct(mock_product_service)


@pytest.mark.asyncio
async def test_execute_success(create_product_uc, mock_product_service):
    test_data = {"name": "New Product", "price": 199.90}
    expected_result = {"id": 1, **test_data}
    mock_product_service.create_product.return_value = expected_result
    result = await create_product_uc.execute(test_data)

    mock_product_service.create_product.assert_awaited_once_with(test_data)
    assert result == expected_result


@pytest.mark.asyncio
async def test_execute_propagates_errors(create_product_uc, mock_product_service):
    error = Exception("Database error")
    mock_product_service.create_product.side_effect = error

    with pytest.raises(Exception) as exc_info:
        await create_product_uc.execute({"name": "Invalid"})

    assert exc_info.value is error
