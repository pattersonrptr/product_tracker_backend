from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import ANY, Mock

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.product import Product
from app.repositories.product_repository import ProductRepository


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

    mock_db.add.side_effect = IntegrityError(
        "Unique constraint failed", params={}, orig=Exception()
    )
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
    mock_product = Product(
        id=product_id, url="http://product1.com", title="Product 1", price=100.0
    )

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


def test_update_product_success(product_repository, mock_db):
    product_id = 1
    update_data = {
        "title": "New title",
        "price": 150.0,
        "url": "https://www.testurl.com",
    }
    mock_product = Product(
        id=product_id, url="http://example.com", title="Old Product", price=100.0
    )

    product_repository.get_by_id = Mock(return_value=mock_product)
    mock_db.commit = Mock()
    mock_db.refresh = Mock()

    result = product_repository.update(product_id, update_data)

    product_repository.get_by_id.assert_called_once_with(product_id)
    assert mock_product.url == update_data["url"]
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
    mock_product = Product(
        id=product_id, url="http://example.com", title="Product", price=100.0
    )

    product_repository.get_by_id = Mock(return_value=mock_product)
    mock_db.commit.side_effect = Exception("Database error")
    mock_db.rollback = Mock()

    with pytest.raises(Exception, match="Database error"):
        product_repository.update(product_id, update_data)

    mock_db.rollback.assert_called_once()


def test_delete_product_success(product_repository, mock_db):
    product_id = 1
    mock_product = Product(
        id=product_id, url="http://example.com", title="Product", price=100.0
    )

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
    mock_product = Product(
        id=product_id, url="http://example.com", title="Product", price=100.0
    )

    product_repository.get_by_id = Mock(return_value=mock_product)
    mock_db.commit.side_effect = Exception("Database error")
    mock_db.rollback = Mock()

    with pytest.raises(Exception, match="Database error"):
        product_repository.delete(product_id)

    mock_db.rollback.assert_called_once()


def test_search_products(product_repository, mock_db):
    query = "test"
    mock_product1 = Product(id=1, title="Test Product 1", price=10.0)
    mock_product2 = Product(id=2, title="Test Product 2", price=20.0)

    query_mock = Mock()
    filter_mock = Mock()
    query_mock.filter.return_value = filter_mock
    filter_mock.all.return_value = [mock_product1, mock_product2]
    mock_db.query.return_value = query_mock

    result = product_repository.search_products(query)

    mock_db.query.assert_called_once_with(Product)
    query_mock.filter.assert_called_once()
    filter_mock.all.assert_called_once()

    assert result == [mock_product1, mock_product2]

    for product in result:
        assert isinstance(product.price, float)


def test_filter_products_with_url(product_repository, mock_db):
    filter_data = {"url": "example.com"}
    mock_product = Product(id=1, url="http://example.com", title="Product", price=10.0)

    query_mock = Mock()
    query_mock.filter.return_value = query_mock
    query_mock.all.return_value = [mock_product]
    mock_db.query.return_value = query_mock

    result = product_repository.filter_products(filter_data)

    mock_db.query.assert_called_once_with(Product)
    query_mock.filter.assert_called_once()
    query_mock.all.assert_called_once()
    assert result == [mock_product]

    for product in result:
        if hasattr(product, "price"):
            assert isinstance(product.price, float)


def test_filter_products_with_price_range(product_repository, mock_db):
    filter_data = {"min_price": 10.0, "max_price": 20.0}
    mock_product1 = Product(id=1, title="Product 1", price=10.0)
    mock_product2 = Product(id=2, title="Product 2", price=15.0)

    query_mock = Mock()
    query_mock.filter.return_value = query_mock
    query_mock.all.return_value = [mock_product1, mock_product2]
    mock_db.query.return_value = query_mock

    result = product_repository.filter_products(filter_data)

    mock_db.query.assert_called_once_with(Product)
    assert query_mock.filter.call_count == 2
    query_mock.all.assert_called_once()
    assert result == [mock_product1, mock_product2]

    filter_calls = [
        str(call[0][0]).lower() for call in query_mock.filter.call_args_list
    ]

    assert any(">=" in call for call in filter_calls)
    assert any("<=" in call for call in filter_calls)
    assert all("price" in call for call in filter_calls)


def test_filter_products_with_date_filters(product_repository, mock_db):
    test_date = datetime(2023, 1, 1, tzinfo=UTC)
    filter_data = {"created_after": test_date, "updated_before": test_date}

    query_mock = Mock()
    query_mock.filter.return_value = query_mock
    query_mock.all.return_value = []
    mock_db.query.return_value = query_mock

    result = product_repository.filter_products(filter_data)

    mock_db.query.assert_called_once_with(Product)
    assert query_mock.filter.call_count == 2
    query_mock.all.assert_called_once()
    assert result == []

    filter_calls = [
        str(call[0][0]).lower() for call in query_mock.filter.call_args_list
    ]

    assert any("created_at" in call and ">=" in call for call in filter_calls)
    assert any("updated_at" in call and "<=" in call for call in filter_calls)


def test_get_product_stats(product_repository, mock_db):
    mock_stats = Mock()
    mock_stats.total_products = 2
    mock_stats.average_price = Decimal("15.0")
    mock_stats.min_price = Decimal("10.0")
    mock_stats.max_price = Decimal("20.0")

    query_mock = Mock()
    query_mock.first.return_value = mock_stats
    mock_db.query.return_value = query_mock

    result = product_repository.get_product_stats()

    mock_db.query.assert_called_once()
    query_mock.first.assert_called_once()
    assert result == {
        "total_products": 2,
        "average_price": 15.0,
        "min_price": 10.0,
        "max_price": 20.0,
    }


def test_get_minimal_products(product_repository, mock_db):
    mock_products = [
        Mock(id=1, title="Product 1", price=Decimal("10.0")),
        Mock(id=2, title="Product 2", price=Decimal("20.0")),
    ]

    query_mock = Mock()
    query_mock.all.return_value = mock_products
    mock_db.query.return_value = query_mock

    result = product_repository.get_minimal_products()

    mock_db.query.assert_called_once_with(Product.id, Product.title, Product.price)
    query_mock.all.assert_called_once()
    assert result == [
        {"id": 1, "title": "Product 1", "price": 10.0},
        {"id": 2, "title": "Product 2", "price": 20.0},
    ]


def test_get_all_products_with_decimal_prices(product_repository, mock_db):
    # Configura produtos com preços Decimal
    from decimal import Decimal

    mock_product1 = Product(id=1, title="Product 1", price=Decimal("10.50"))
    mock_product2 = Product(id=2, title="Product 2", price=Decimal("20.75"))

    mock_db.query.return_value.all.return_value = [mock_product1, mock_product2]

    result = product_repository.get_all()

    # Verifica se os preços foram convertidos para float
    assert isinstance(result[0].price, float)
    assert result[0].price == 10.5
    assert isinstance(result[1].price, float)
    assert result[1].price == 20.75


def test_get_by_id_with_decimal_price(product_repository, mock_db):
    from decimal import Decimal

    mock_product = Product(id=1, title="Product", price=Decimal("15.99"))

    query_mock = Mock()
    filter_mock = Mock()
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = mock_product
    mock_db.query.return_value = query_mock

    result = product_repository.get_by_id(1)

    assert isinstance(result.price, float)
    assert result.price == 15.99


def test_get_by_url_with_decimal_price(product_repository, mock_db):
    from decimal import Decimal

    mock_product = Product(
        id=1, url="http://test.com", title="Product", price=Decimal("12.34")
    )

    query_mock = Mock()
    filter_mock = Mock()
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = mock_product
    mock_db.query.return_value = query_mock

    result = product_repository.get_by_url("http://test.com")

    assert isinstance(result.price, float)
    assert result.price == 12.34


def test_update_with_decimal_price(product_repository, mock_db):
    from decimal import Decimal

    mock_product = Product(id=1, title="Product", price=Decimal("10.0"))
    update_data = {"price": Decimal("15.0")}

    product_repository.get_by_id = Mock(return_value=mock_product)
    mock_db.commit = Mock()
    mock_db.refresh = Mock()

    result = product_repository.update(1, update_data)

    assert isinstance(result.price, float)
    assert result.price == 15.0


def test_search_products_with_decimal_prices(product_repository, mock_db):
    from decimal import Decimal

    mock_product = Product(id=1, title="Test", price=Decimal("9.99"))

    query_mock = Mock()
    filter_mock = Mock()
    query_mock.filter.return_value = filter_mock
    filter_mock.all.return_value = [mock_product]
    mock_db.query.return_value = query_mock

    result = product_repository.search_products("test")

    assert isinstance(result[0].price, float)
    assert result[0].price == 9.99


def test_filter_products_with_decimal_prices(product_repository, mock_db):
    from decimal import Decimal

    mock_product = Product(id=1, title="Product", price=Decimal("19.99"))

    query_mock = Mock()
    query_mock.filter.return_value = query_mock
    query_mock.all.return_value = [mock_product]
    mock_db.query.return_value = query_mock

    result = product_repository.filter_products({"min_price": 10.0})

    assert isinstance(result[0].price, float)
    assert result[0].price == 19.99


def test_filter_products_with_title(product_repository, mock_db):
    filter_data = {"title": "test"}
    mock_product = Product(id=1, title="Test Product", price=10.0)

    query_mock = Mock()
    query_mock.filter.return_value = query_mock
    query_mock.all.return_value = [mock_product]
    mock_db.query.return_value = query_mock

    result = product_repository.filter_products(filter_data)

    mock_db.query.assert_called_once_with(Product)
    assert query_mock.filter.call_count == 1
    query_mock.all.assert_called_once()
    assert result == [mock_product]


def test_filter_products_with_created_before(product_repository, mock_db):
    test_date = datetime(2023, 1, 1, tzinfo=UTC)
    filter_data = {"created_before": test_date}

    query_mock = Mock()
    query_mock.filter.return_value = query_mock
    query_mock.all.return_value = []
    mock_db.query.return_value = query_mock

    result = product_repository.filter_products(filter_data)

    mock_db.query.assert_called_once_with(Product)
    assert query_mock.filter.call_count == 1
    query_mock.all.assert_called_once()
    assert result == []


def test_filter_products_with_updated_after(product_repository, mock_db):
    test_date = datetime(2023, 1, 1, tzinfo=UTC)
    filter_data = {"updated_after": test_date}

    query_mock = Mock()
    query_mock.filter.return_value = query_mock
    query_mock.all.return_value = []
    mock_db.query.return_value = query_mock

    result = product_repository.filter_products(filter_data)

    mock_db.query.assert_called_once_with(Product)
    assert query_mock.filter.call_count == 1
    query_mock.all.assert_called_once()
    assert result == []
