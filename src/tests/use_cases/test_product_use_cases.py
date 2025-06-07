from unittest.mock import MagicMock
from datetime import datetime, timezone

from src.app.entities.product import Product as ProductEntity
from src.app.entities.price_history import PriceHistory as PriceHistoryEntity
from src.app.use_cases.product_use_cases import (
    CreateProductUseCase,
    GetProductByIdUseCase,
    GetProductByUrlUseCase,
    DeleteProductUseCase,
)
from src.app.use_cases.product_use_cases import UpdateProductUseCase
from src.app.interfaces.schemas.product_schema import ProductUpdate


def test_create_product_use_case_success_with_initial_price():
    product_repo_mock = MagicMock()
    price_history_repo_mock = MagicMock()
    product_input = ProductEntity(
        url="http://example.com/product/1",
        title="Sample Product",
        source_website_id=1,
        description="A cool sample product.",
    )
    initial_price = 199.99
    mock_created_product = ProductEntity(
        id=101,
        url=product_input.url,
        title=product_input.title,
        source_website_id=product_input.source_website_id,
        description=product_input.description,
        is_available=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    product_repo_mock.create.return_value = mock_created_product
    mock_retrieved_product = ProductEntity(
        id=101,
        url=product_input.url,
        title=product_input.title,
        source_website_id=product_input.source_website_id,
        description=product_input.description,
        is_available=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        current_price=initial_price,
    )
    product_repo_mock.get_by_id.return_value = mock_retrieved_product
    use_case = CreateProductUseCase(product_repo_mock, price_history_repo_mock)
    result = use_case.execute(product_input, initial_price)
    product_repo_mock.create.assert_called_once_with(product_input)
    price_history_repo_mock.create.assert_called_once()
    called_price_history_entry = price_history_repo_mock.create.call_args[0][0]
    assert isinstance(called_price_history_entry, PriceHistoryEntity)
    assert called_price_history_entry.product_id == mock_created_product.id
    assert called_price_history_entry.price == initial_price
    product_repo_mock.get_by_id.assert_called_once_with(mock_created_product.id)
    assert result == mock_retrieved_product


def test_create_product_use_case_success_no_initial_price():
    product_repo_mock = MagicMock()
    price_history_repo_mock = MagicMock()
    product_input = ProductEntity(
        url="http://example.com/product/no-price",
        title="Product Without Initial Price",
        source_website_id=2,
        description="A product with no price yet.",
    )
    initial_price = None
    mock_created_product = ProductEntity(
        id=102,
        url=product_input.url,
        title=product_input.title,
        source_website_id=product_input.source_website_id,
        description=product_input.description,
        is_available=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    product_repo_mock.create.return_value = mock_created_product
    use_case = CreateProductUseCase(product_repo_mock, price_history_repo_mock)
    result = use_case.execute(product_input, initial_price)
    product_repo_mock.create.assert_called_once_with(product_input)
    price_history_repo_mock.create.assert_not_called()
    product_repo_mock.get_by_id.assert_not_called()
    assert result == mock_created_product


def test_get_product_by_id_use_case_success():
    product_repo_mock = MagicMock()
    product_id_to_find = 101
    mock_product_entity = ProductEntity(
        id=product_id_to_find,
        url="http://example.com/product/found",
        title="Found Product",
        source_website_id=1,
        description="This product was found.",
        is_available=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    product_repo_mock.get_by_id.return_value = mock_product_entity
    use_case = GetProductByIdUseCase(product_repo_mock)
    result = use_case.execute(product_id_to_find)
    product_repo_mock.get_by_id.assert_called_once_with(product_id_to_find)
    assert result == mock_product_entity


def test_get_product_by_id_use_case_not_found():
    product_repo_mock = MagicMock()
    product_id_to_find = 999
    product_repo_mock.get_by_id.return_value = None
    use_case = GetProductByIdUseCase(product_repo_mock)
    result = use_case.execute(product_id_to_find)
    product_repo_mock.get_by_id.assert_called_once_with(product_id_to_find)
    assert result is None


def test_get_product_by_url_use_case_success():
    product_repo_mock = MagicMock()
    url_to_find = "http://example.com/product/unique-url"
    mock_product_entity = ProductEntity(
        id=201,
        url=url_to_find,
        title="URL Found Product",
        source_website_id=1,
        description="This product was found by URL.",
        is_available=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    product_repo_mock.get_by_url.return_value = mock_product_entity
    use_case = GetProductByUrlUseCase(product_repo_mock)
    result = use_case.execute(url_to_find)
    product_repo_mock.get_by_url.assert_called_once_with(url_to_find)
    assert result == mock_product_entity


def test_get_product_by_url_use_case_not_found():
    product_repo_mock = MagicMock()
    url_to_find = "http://example.com/product/non-existent-url"
    product_repo_mock.get_by_url.return_value = None
    use_case = GetProductByUrlUseCase(product_repo_mock)
    result = use_case.execute(url_to_find)
    product_repo_mock.get_by_url.assert_called_once_with(url_to_find)
    assert result is None


def test_update_product_use_case_success_no_new_price():
    product_repo_mock = MagicMock()
    price_history_repo_mock = MagicMock()
    product_id_to_update = 1

    original_product = ProductEntity(
        id=product_id_to_update,
        url="http://original.com/product",
        title="Original Title",
        source_website_id=1,
        description="Original description",
        is_available=True,
        city="Original City",
        state="Original State",
        created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
    )
    product_update_data = ProductUpdate(
        url=original_product.url,
        title="Updated Product Title",
        description="New description",
        source_website_id=original_product.source_website_id,
        city=original_product.city,
        state=original_product.state,
    )
    updated_product_entity = ProductEntity(
        id=product_id_to_update,
        url=product_update_data.url,
        title=product_update_data.title,
        source_website_id=product_update_data.source_website_id,
        description=product_update_data.description,
        is_available=original_product.is_available,
        city=product_update_data.city,
        state=product_update_data.state,
        created_at=original_product.created_at,
        updated_at=datetime.now(timezone.utc),
        current_price=original_product.current_price,
    )
    product_repo_mock.update.return_value = updated_product_entity
    product_repo_mock.get_by_id.return_value = original_product
    use_case = UpdateProductUseCase(product_repo_mock, price_history_repo_mock)
    result = use_case.execute(product_id_to_update, product_update_data, new_price=None)
    product_repo_mock.get_by_id.assert_called_once_with(product_id_to_update)
    product_repo_mock.update.assert_called_once()
    called_args, _ = product_repo_mock.update.call_args
    assert called_args[0] == product_id_to_update
    updated_entity_passed_to_repo = called_args[1]
    assert isinstance(updated_entity_passed_to_repo, ProductEntity)
    assert updated_entity_passed_to_repo.title == product_update_data.title
    assert updated_entity_passed_to_repo.description == product_update_data.description
    assert updated_entity_passed_to_repo.url == product_update_data.url
    assert (
        updated_entity_passed_to_repo.source_website_id
        == product_update_data.source_website_id
    )
    assert updated_entity_passed_to_repo.city == product_update_data.city
    assert updated_entity_passed_to_repo.state == product_update_data.state
    assert updated_entity_passed_to_repo.created_at == original_product.created_at

    price_history_repo_mock.create.assert_not_called()
    assert result == updated_product_entity


def test_delete_product_use_case_success():
    """
    Testa a exclusão bem-sucedida de um produto.
    """
    product_repo_mock = MagicMock()

    product_id_to_delete = 1

    # Configura o mock para retornar True, indicando que a exclusão foi bem-sucedida
    product_repo_mock.delete.return_value = True

    use_case = DeleteProductUseCase(product_repo_mock)

    # Executa o caso de uso
    result = use_case.execute(product_id_to_delete)

    # Asserções
    # Verifica se o método 'delete' do repositório foi chamado uma vez com o ID correto
    product_repo_mock.delete.assert_called_once_with(product_id_to_delete)

    # Verifica se o caso de uso retornou True
    assert result is True
