from datetime import datetime, timezone
import pytest
from unittest.mock import MagicMock

from src.app.infrastructure.repositories.product_repository import ProductRepository
from src.app.entities.product import Product as ProductEntity
from src.app.infrastructure.database.models.product_model import Product as ProductModel
from src.app.infrastructure.database.models.product_model import ProductCondition


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def repo(mock_db):
    return ProductRepository(mock_db)


@pytest.fixture
def product_entity():
    return ProductEntity(
        id=1,
        url="http://example.com/test-product",
        title="Test Product Title",
        source_website_id=1,
        description="This is a test product description.",
        source_product_code="ABCDEF123",
        city="Sao Paulo",
        state="SP",
        condition=ProductCondition.NEW,
        seller_name="Test Seller",
        is_available=True,
        image_urls="http://example.com/img1.jpg,http://example.com/img2.jpg",
        source_metadata={"category": "electronics", "brand": "testbrand"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        current_price=199.99,
    )


def test_create_product(repo, mock_db, product_entity, mocker):
    mock_db.refresh.side_effect = (
        lambda obj: setattr(obj, "id", product_entity.id)
        or setattr(obj, "created_at", product_entity.created_at)
        or setattr(obj, "updated_at", product_entity.updated_at)
        or obj
    )

    created_product = repo.create(product_entity)

    mock_db.add.assert_called_once()
    assert isinstance(mock_db.add.call_args[0][0], ProductModel)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_db.add.call_args[0][0])

    assert isinstance(created_product, ProductEntity)
    assert created_product.id == product_entity.id
    assert created_product.title == product_entity.title
    assert created_product.url == product_entity.url
    assert created_product.source_website_id == product_entity.source_website_id
    assert created_product.created_at == product_entity.created_at
    assert created_product.updated_at == product_entity.updated_at
    assert created_product.description == product_entity.description
    assert created_product.condition == product_entity.condition


def test_get_all_products(repo, mock_db, product_entity, mocker):
    mock_db_product_model = mocker.Mock(
        id=product_entity.id,
        url=product_entity.url,
        title=product_entity.title,
        source_website_id=product_entity.source_website_id,
        description=product_entity.description,
        source_product_code=product_entity.source_product_code,
        city=product_entity.city,
        state=product_entity.state,
        condition=product_entity.condition,
        seller_name=product_entity.seller_name,
        is_available=product_entity.is_available,
        image_urls=product_entity.image_urls,
        source_metadata=product_entity.source_metadata,
        created_at=product_entity.created_at,
        updated_at=product_entity.updated_at,
        price_history=[
            mocker.Mock(
                id=1,
                price=product_entity.current_price,
                product_id=product_entity.id,
                created_at=datetime.now(timezone.utc),
            )
        ],
    )

    mock_db_product_model.__dict__ = {
        "id": mock_db_product_model.id,
        "url": mock_db_product_model.url,
        "title": mock_db_product_model.title,
        "source_website_id": mock_db_product_model.source_website_id,
        "description": mock_db_product_model.description,
        "source_product_code": mock_db_product_model.source_product_code,
        "city": mock_db_product_model.city,
        "state": mock_db_product_model.state,
        "condition": mock_db_product_model.condition,
        "seller_name": mock_db_product_model.seller_name,
        "is_available": mock_db_product_model.is_available,
        "image_urls": mock_db_product_model.image_urls,
        "source_metadata": mock_db_product_model.source_metadata,
        "created_at": mock_db_product_model.created_at,
        "updated_at": mock_db_product_model.updated_at,
        "price_history": mock_db_product_model.price_history,
    }

    mock_db.query.return_value.options.return_value.limit.return_value.offset.return_value.all.return_value = [
        mock_db_product_model
    ]
    mock_db.query.return_value.count.return_value = 1

    products, total = repo.get_all(offset=0, limit=10)

    mock_db.query.assert_called_once()
    mock_db.query().options.assert_called_once()

    assert len(products) == 1
    assert total == 1
    assert isinstance(products[0], ProductEntity)
    assert products[0].id == product_entity.id
    assert products[0].title == product_entity.title
    assert products[0].url == product_entity.url
    assert products[0].source_website_id == product_entity.source_website_id
    assert products[0].current_price == product_entity.current_price


def test_get_by_id_found(repo, mock_db, product_entity, mocker):
    mock_db_product_model = mocker.Mock(
        spec=ProductModel,
        id=product_entity.id,
        url=product_entity.url,
        title=product_entity.title,
        source_website_id=product_entity.source_website_id,
        description=product_entity.description,
        source_product_code=product_entity.source_product_code,
        city=product_entity.city,
        state=product_entity.state,
        condition=product_entity.condition,
        seller_name=product_entity.seller_name,
        is_available=product_entity.is_available,
        image_urls=product_entity.image_urls,
        source_metadata=product_entity.source_metadata,
        created_at=product_entity.created_at,
        updated_at=product_entity.updated_at,
        price_history=[
            mocker.Mock(
                id=1,
                price=product_entity.current_price,
                product_id=product_entity.id,
                created_at=datetime.now(timezone.utc),
            )
        ],
    )

    mock_db_product_model.__dict__.update(
        {
            "id": mock_db_product_model.id,
            "url": mock_db_product_model.url,
            "title": mock_db_product_model.title,
            "source_website_id": mock_db_product_model.source_website_id,
            "description": mock_db_product_model.description,
            "source_product_code": mock_db_product_model.source_product_code,
            "city": mock_db_product_model.city,
            "state": mock_db_product_model.state,
            "condition": mock_db_product_model.condition,
            "seller_name": mock_db_product_model.seller_name,
            "is_available": mock_db_product_model.is_available,
            "image_urls": mock_db_product_model.image_urls,
            "source_metadata": mock_db_product_model.source_metadata,
            "created_at": mock_db_product_model.created_at,
            "updated_at": mock_db_product_model.updated_at,
            "price_history": mock_db_product_model.price_history,
        }
    )

    mock_query_result = mock_db.query.return_value
    mock_options_result = mock_query_result.options.return_value
    mock_filter_result = mock_options_result.filter.return_value
    mock_filter_result.first.return_value = mock_db_product_model

    found_product = repo.get_by_id(product_entity.id)

    mock_db.query.assert_called_once_with(ProductModel)
    mock_query_result.options.assert_called_once()
    mock_options_result.filter.assert_called_once()

    assert found_product is not None
    assert isinstance(found_product, ProductEntity)
    assert found_product.id == product_entity.id
    assert found_product.title == product_entity.title
    assert found_product.url == product_entity.url
    assert found_product.source_website_id == product_entity.source_website_id
    assert found_product.current_price == product_entity.current_price
    assert found_product.created_at == product_entity.created_at
    assert found_product.updated_at == product_entity.updated_at


def test_get_by_id_not_found(repo, mock_db, mocker):
    mock_query_result = mock_db.query.return_value
    mock_options_result = mock_query_result.options.return_value
    mock_filter_result = mock_options_result.filter.return_value
    mock_filter_result.first.return_value = None

    non_existent_id = 999
    found_product = repo.get_by_id(non_existent_id)

    mock_db.query.assert_called_once_with(ProductModel)
    mock_query_result.options.assert_called_once()
    mock_options_result.filter.assert_called_once()
    mock_filter_result.first.assert_called_once()

    assert found_product is None


def test_update_product(repo, mock_db, product_entity, mocker):
    mock_db_product_model = mocker.Mock(
        spec=ProductModel,
        id=product_entity.id,
        url=product_entity.url,
        title=product_entity.title,
        source_website_id=product_entity.source_website_id,
        description=product_entity.description,
        source_product_code=product_entity.source_product_code,
        city=product_entity.city,
        state=product_entity.state,
        condition=product_entity.condition,
        seller_name=product_entity.seller_name,
        is_available=product_entity.is_available,
        image_urls=product_entity.image_urls,
        source_metadata=product_entity.source_metadata,
        created_at=product_entity.created_at,
        updated_at=product_entity.updated_at,
        price_history=[
            mocker.Mock(
                id=1,
                price=product_entity.current_price,
                product_id=product_entity.id,
                created_at=datetime.now(timezone.utc),
            )
        ],
    )

    mock_db_product_model.__dict__.update(
        {
            "id": mock_db_product_model.id,
            "url": mock_db_product_model.url,
            "title": mock_db_product_model.title,
            "source_website_id": mock_db_product_model.source_website_id,
            "description": mock_db_product_model.description,
            "source_product_code": mock_db_product_model.source_product_code,
            "city": mock_db_product_model.city,
            "state": mock_db_product_model.state,
            "condition": mock_db_product_model.condition,
            "seller_name": mock_db_product_model.seller_name,
            "is_available": mock_db_product_model.is_available,
            "image_urls": mock_db_product_model.image_urls,
            "source_metadata": mock_db_product_model.source_metadata,
            "created_at": mock_db_product_model.created_at,
            "updated_at": mock_db_product_model.updated_at,
            "price_history": mock_db_product_model.price_history,
        }
    )

    mock_db.query.return_value.filter.return_value.first.return_value = (
        mock_db_product_model
    )
    mock_db.refresh.side_effect = lambda obj: obj
    updated_title = "Updated Product Title"
    updated_description = "This is an updated description."
    product_update_entity = ProductEntity(
        id=product_entity.id,
        url=product_entity.url,
        title=updated_title,
        source_website_id=product_entity.source_website_id,
        description=updated_description,
        source_product_code=product_entity.source_product_code,
        city=product_entity.city,
        state=product_entity.state,
        condition=product_entity.condition,
        seller_name=product_entity.seller_name,
        is_available=product_entity.is_available,
        image_urls=product_entity.image_urls,
        source_metadata=product_entity.source_metadata,
        created_at=product_entity.created_at,
        updated_at=datetime.now(timezone.utc),
        current_price=product_entity.current_price,
    )

    updated_product = repo.update(product_entity.id, product_update_entity)
    mock_db.query.assert_called_once()
    mock_db.query().filter.assert_called_once()
    mock_db.query().filter().first.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_db_product_model)

    assert mock_db_product_model.title == updated_title
    assert mock_db_product_model.description == updated_description
    assert mock_db_product_model.updated_at is not None

    assert updated_product is not None
    assert isinstance(updated_product, ProductEntity)
    assert updated_product.id == product_entity.id
    assert updated_product.title == updated_title
    assert updated_product.description == updated_description
    assert updated_product.updated_at is not None
    assert updated_product.updated_at != product_entity.updated_at
    assert updated_product.url == product_entity.url
    assert updated_product.source_website_id == product_entity.source_website_id


def test_delete_product(repo, mock_db, product_entity, mocker):
    mock_db_product_model = mocker.Mock(
        spec=ProductModel,
        id=product_entity.id,
        url=product_entity.url,
        title=product_entity.title,
        source_website_id=product_entity.source_website_id,
        description=product_entity.description,
        source_product_code=product_entity.source_product_code,
        city=product_entity.city,
        state=product_entity.state,
        condition=product_entity.condition,
        seller_name=product_entity.seller_name,
        is_available=product_entity.is_available,
        image_urls=product_entity.image_urls,
        source_metadata=product_entity.source_metadata,
        created_at=product_entity.created_at,
        updated_at=product_entity.updated_at,
    )

    mock_db_product_model.__dict__.update(
        {
            "id": mock_db_product_model.id,
            "url": mock_db_product_model.url,
            "title": mock_db_product_model.title,
            "source_website_id": mock_db_product_model.source_website_id,
            "description": mock_db_product_model.description,
            "source_product_code": mock_db_product_model.source_product_code,
            "city": mock_db_product_model.city,
            "state": mock_db_product_model.state,
            "condition": mock_db_product_model.condition,
            "seller_name": mock_db_product_model.seller_name,
            "is_available": mock_db_product_model.is_available,
            "image_urls": mock_db_product_model.image_urls,
            "source_metadata": mock_db_product_model.source_metadata,
            "created_at": mock_db_product_model.created_at,
            "updated_at": mock_db_product_model.updated_at,
        }
    )

    mock_db.query.return_value.filter.return_value.first.return_value = (
        mock_db_product_model
    )
    deleted_successfully = repo.delete(product_entity.id)

    mock_db.query.assert_called_once_with(ProductModel)
    mock_db.query().filter.assert_called_once()
    mock_db.query().filter().first.assert_called_once()
    mock_db.delete.assert_called_once_with(mock_db_product_model)
    mock_db.commit.assert_called_once()

    assert deleted_successfully is True


def test_delete_product_not_found(repo, mock_db, mocker):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    non_existent_id = 999
    deleted_successfully = repo.delete(non_existent_id)
    mock_db.query.assert_called_once_with(ProductModel)
    mock_db.query().filter.assert_called_once()
    mock_db.query().filter().first.assert_called_once()
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()

    assert deleted_successfully is False
