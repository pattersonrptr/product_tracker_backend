import pytest
from unittest.mock import Mock, ANY
from sqlalchemy.exc import IntegrityError
from datetime import datetime, UTC
from app.repositories.product_repository import ProductRepository
from app.models.product_models import Product



@pytest.fixture
def mock_db():
    db = Mock()
    db.commit = Mock()
    db.refresh = Mock()
    db.add = Mock()
    db.delete = Mock()
    db.query = Mock()
    db.rollback = Mock()
    return db

@pytest.fixture
def product_repository(mock_db):
    return ProductRepository(mock_db)

def test_create_product_success(product_repository, mock_db):
    test_data = {"url": "http://example.com", "title": "Test Product", "price": 99.99}

    result = product_repository.create(test_data)

    mock_db.add.assert_called_once()
    added_product = mock_db.add.call_args[0][0]

    assert isinstance(added_product, Product)
    assert added_product.url == test_data["url"]
    assert added_product.title == test_data["title"]
    assert added_product.price == test_data["price"]

    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(added_product)
    assert result == added_product

def test_create_product_with_integrity_error(product_repository, mock_db):
    test_data = {"url": "http://example.com", "title": "Test Product", "price": 99.99}

    mock_db.add.side_effect = IntegrityError("Unique constraint failed", params={}, orig=Exception())
    mock_db.rollback = Mock()

    with pytest.raises(IntegrityError):
        product_repository.create(test_data)

    mock_db.rollback.assert_called_once()

def test_get_all_products_success(product_repository, mock_db):
    mock_product1 = Product(url="http://product1.com", title="Product 1", price=100.0)
    mock_product2 = Product(url="http://product2.com", title="Product 2", price=200.0)

    mock_db.query.return_value.all.return_value = [mock_product1, mock_product2]

    result = product_repository.get_all()

    mock_db.query.assert_called_once_with(Product)
    assert result == [mock_product1, mock_product2]
    assert len(result) == 2

def test_get_all_products_empty(product_repository, mock_db):
    mock_db.query.return_value.all.return_value = []

    result = product_repository.get_all()

    mock_db.query.assert_called_once_with(Product)
    assert result == []
    assert len(result) == 0

def test_get_by_id_found(product_repository, mock_db):
    product_id = 1
    mock_product = Product(id=product_id, url="http://product1.com", title="Product 1", price=100.0)

    query_mock = Mock()
    filter_mock = Mock()
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = mock_product
    mock_db.query.return_value = query_mock

    result = product_repository.get_by_id(product_id)

    mock_db.query.assert_called_once_with(Product)
    query_mock.filter.assert_called_once_with(ANY)
    filter_mock.first.assert_called_once()
    assert result == mock_product

    filter_call = query_mock.filter.call_args[0][0]
    assert str(filter_call) == str(Product.id == product_id)

def test_get_by_id_not_found(product_repository, mock_db):
    product_id = 999

    query_mock = Mock()
    filter_mock = Mock()
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = None
    mock_db.query.return_value = query_mock

    result = product_repository.get_by_id(product_id)

    mock_db.query.assert_called_once_with(Product)
    query_mock.filter.assert_called_once_with(ANY)
    filter_mock.first.assert_called_once()
    assert result is None

    filter_call = query_mock.filter.call_args[0][0]
    assert str(filter_call) == str(Product.id == product_id)

def test_get_by_url_found(product_repository, mock_db):
    url = "http://example.com"
    mock_product = Product(url=url, title="Product", price=100.0)

    query_mock = Mock()
    filter_mock = Mock()
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = mock_product
    mock_db.query.return_value = query_mock

    result = product_repository.get_by_url(url)

    mock_db.query.assert_called_once_with(Product)
    query_mock.filter.assert_called_once_with(ANY)
    filter_mock.first.assert_called_once()
    assert result == mock_product

    filter_call = query_mock.filter.call_args[0][0]
    assert str(filter_call) == str(Product.url == url)

def test_get_by_url_not_found(product_repository, mock_db):
    url = "http://nonexistent.com"

    query_mock = Mock()
    filter_mock = Mock()
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = None
    mock_db.query.return_value = query_mock

    result = product_repository.get_by_url(url)

    mock_db.query.assert_called_once_with(Product)
    query_mock.filter.assert_called_once_with(ANY)
    filter_mock.first.assert_called_once()
    assert result is None

    filter_call = query_mock.filter.call_args[0][0]
    assert str(filter_call) == str(Product.url == url)

def test_get_products_older_than_found(product_repository, mock_db):
    cutoff_date = datetime.now(UTC)
    mock_product = Product(url="http://example.com", title="Product", price=100.0, updated_at=datetime(2022, 1, 1, tzinfo=UTC))

    query_mock = Mock()
    filter_mock = Mock()
    query_mock.filter.return_value = filter_mock
    filter_mock.all.return_value = [mock_product]
    mock_db.query.return_value = query_mock

    result = product_repository.get_products_older_than(cutoff_date)

    mock_db.query.assert_called_once_with(Product)
    query_mock.filter.assert_called_once_with(ANY)
    filter_mock.all.assert_called_once()
    assert result == [mock_product]

    filter_call = query_mock.filter.call_args[0][0]
    assert str(filter_call) == str(Product.updated_at < cutoff_date)

def test_get_products_older_than_not_found(product_repository, mock_db):
    cutoff_date = datetime.now(UTC)

    query_mock = Mock()
    filter_mock = Mock()
    query_mock.filter.return_value = filter_mock
    filter_mock.all.return_value = []
    mock_db.query.return_value = query_mock

    result = product_repository.get_products_older_than(cutoff_date)

    mock_db.query.assert_called_once_with(Product)
    query_mock.filter.assert_called_once_with(ANY)
    filter_mock.all.assert_called_once()
    assert result == []

    filter_call = query_mock.filter.call_args[0][0]
    assert str(filter_call) == str(Product.updated_at < cutoff_date)

def test_update_product_success(product_repository, mock_db):
    product_id = 1
    update_data = {"title": "New title", "price": 150.0}
    mock_product = Product(id=product_id, url="http://example.com", title="Old Product", price=100.0)

    product_repository.get_by_id = Mock(return_value=mock_product)
    mock_db.commit = Mock()
    mock_db.refresh = Mock()

    result = product_repository.update(product_id, update_data)

    product_repository.get_by_id.assert_called_once_with(product_id)
    assert mock_product.title == update_data["title"]
    assert mock_product.price == update_data["price"]
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_product)
    assert result == mock_product

def test_update_product_not_found(product_repository, mock_db):
    product_id = 999
    update_data = {"title": "Non-existent title"}

    product_repository.get_by_id = Mock(return_value=None)

    result = product_repository.update(product_id, update_data)

    product_repository.get_by_id.assert_called_once_with(product_id)
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()
    assert result is None

def test_update_product_database_error(product_repository, mock_db):
    product_id = 1
    update_data = {"title": "Database error"}
    mock_product = Product(id=product_id, url="http://example.com", title="Product", price=100.0)

    product_repository.get_by_id = Mock(return_value=mock_product)
    mock_db.commit.side_effect = Exception("Database error")
    mock_db.rollback = Mock()

    with pytest.raises(Exception, match="Database error"):
        product_repository.update(product_id, update_data)

    mock_db.rollback.assert_called_once()

def test_update_by_url_success(product_repository, mock_db):
    url = "http://example.com"
    update_data = {"title": "New title", "price": 150.0}
    mock_product = Product(url=url, title="Old Product", price=100.0)

    product_repository.get_by_url = Mock(return_value=mock_product)
    mock_db.commit = Mock()
    mock_db.refresh = Mock()

    result = product_repository.update_by_url(url, update_data)

    product_repository.get_by_url.assert_called_once_with(url)
    assert mock_product.title == update_data["title"]
    assert mock_product.price == update_data["price"]
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_product)
    assert result == mock_product

def test_update_by_url_not_found(product_repository, mock_db):
    url = "http://nonexistent.com"
    update_data = {"title": "Non-existent title"}

    product_repository.get_by_url = Mock(return_value=None)

    result = product_repository.update_by_url(url, update_data)

    product_repository.get_by_url.assert_called_once_with(url)
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()
    assert result is None

def test_update_by_url_database_error(product_repository, mock_db):
    url = "http://example.com"
    update_data = {"title": "Database error"}
    mock_product = Product(url=url, title="Product", price=100.0)

    product_repository.get_by_url = Mock(return_value=mock_product)
    mock_db.commit.side_effect = Exception("Database error")
    mock_db.rollback = Mock()

    with pytest.raises(Exception, match="Database error"):
        product_repository.update_by_url(url, update_data)

    mock_db.rollback.assert_called_once()

def test_delete_product_success(product_repository, mock_db):
    product_id = 1
    mock_product = Product(id=product_id, url="http://example.com", title="Product", price=100.0)

    product_repository.get_by_id = Mock(return_value=mock_product)
    mock_db.delete = Mock()
    mock_db.commit = Mock()

    result = product_repository.delete(product_id)

    product_repository.get_by_id.assert_called_once_with(product_id)
    mock_db.delete.assert_called_once_with(mock_product)
    mock_db.commit.assert_called_once()
    assert result is True

def test_delete_product_not_found(product_repository, mock_db):
    product_id = 999
    product_repository.get_by_id = Mock(return_value=None)

    result = product_repository.delete(product_id)

    product_repository.get_by_id.assert_called_once_with(product_id)
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()
    assert result is None

def test_delete_product_database_error(product_repository, mock_db):
    product_id = 1
    mock_product = Product(id=product_id, url="http://example.com", title="Product", price=100.0)

    product_repository.get_by_id = Mock(return_value=mock_product)
    mock_db.commit.side_effect = Exception("Database error")
    mock_db.rollback = Mock()

    with pytest.raises(Exception, match="Database error"):
        product_repository.delete(product_id)

    mock_db.rollback.assert_called_once()
