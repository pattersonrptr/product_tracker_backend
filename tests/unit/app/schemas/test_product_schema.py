# from datetime import date, datetime
#
# import pytest
# from pydantic import HttpUrl, ValidationError
#
# from app.schemas.product_schema import (
#     ProductBase,
#     ProductBulkCreate,
#     ProductCreate,
#     ProductFilter,
#     ProductPartialResponse,
#     ProductResponse,''
#     ProductSearch,
#     ProductStats,
#     ProductUpdate,
#     parse_price,
# )
#
#
# def test_product_base_valid():
#     product = ProductBase(
#         url="https://example.com/product", title="Sample Product", price=19.99
#     )
#     assert product.url == HttpUrl("https://example.com/product")
#     assert product.title == "Sample Product"
#     assert product.price == 19.99
#
#
# def test_product_base_invalid_price():
#     with pytest.raises(ValidationError):
#         ProductBase(
#             url="https://example.com/product", title="Sample Product", price=-10.0
#         )
#
#
# def test_product_base_price_conversion():
#     product = ProductBase(
#         url="https://example.com/product", title="Sample Product", price="1,999.99"
#     )
#     assert product.price == 1999.99
#
#
# def test_product_create():
#     product = ProductCreate(
#         url="https://example.com/product", title="Sample Product", price=29.99
#     )
#     assert isinstance(product, ProductBase)
#
#
# def test_product_response():
#     product = ProductResponse(
#         id=1,
#         url="https://example.com/product",
#         title="Sample Product",
#         price=39.99,
#         created_at=datetime.now(),
#         updated_at=datetime.now(),
#     )
#     assert product.id == 1
#     assert isinstance(product.created_at, datetime)
#     assert isinstance(product.updated_at, datetime)
#
#
# def test_product_update():
#     update_data = ProductUpdate(title="Updated Product", price=49.99)
#     assert update_data.title == "Updated Product"
#     assert update_data.price == 49.99
#     assert update_data.url is None
#
#
# def test_product_update_price_conversion():
#     update_data = ProductUpdate(price="2,999.99")
#     assert update_data.price == 2999.99
#
#
# def test_product_filter():
#     filter_data = ProductFilter(
#         title="Sample",
#         min_price=10.0,
#         max_price=100.0,
#         created_after=date(2023, 1, 1),
#         created_before=date(2023, 12, 31),
#     )
#     assert filter_data.title == "Sample"
#     assert filter_data.min_price == 10.0
#     assert filter_data.max_price == 100.0
#     assert filter_data.created_after == date(2023, 1, 1)
#     assert filter_data.created_before == date(2023, 12, 31)
#
#
# def test_product_bulk_create():
#     products = [
#         ProductCreate(
#             url="https://example.com/product1", title="Product 1", price=10.0
#         ),
#         ProductCreate(
#             url="https://example.com/product2", title="Product 2", price=20.0
#         ),
#     ]
#     bulk_create = ProductBulkCreate(products=products)
#     assert len(bulk_create.products) == 2
#
#
# def test_product_search():
#     search = ProductSearch(query="Sample")
#     assert search.query == "Sample"
#
#
# def test_product_stats():
#     stats = ProductStats(
#         total_products=100, average_price=50.0, min_price=10.0, max_price=100.0
#     )
#     assert stats.total_products == 100
#     assert stats.average_price == 50.0
#     assert stats.min_price == 10.0
#     assert stats.max_price == 100.0
#
#
# def test_product_partial_response():
#     product = ProductPartialResponse(id=1, title="Sample Product", price=59.99)
#     assert product.id == 1
#     assert product.title == "Sample Product"
#     assert product.price == 59.99
#
#
# def test_product_base_title_min_length():
#     with pytest.raises(ValidationError):
#         ProductBase(url="https://example.com/product", title="", price=19.99)
#
#
# def test_product_base_url_validation():
#     with pytest.raises(ValidationError):
#         ProductBase(url="invalid-url", title="Sample Product", price=19.99)
#
#
# def test_product_filter_invalid_price_range():
#     with pytest.raises(ValidationError):
#         ProductFilter(min_price=-10.0, max_price=-5.0)
#
#
# def test_product_bulk_create_empty_list():
#     with pytest.raises(ValidationError):
#         ProductBulkCreate(products=[])
#
#
# def test_parse_price_non_string():
#     with pytest.raises(ValueError, match="The value should be a string or a number"):
#         parse_price([1, 2, 3])
#
#
# def test_parse_price_multiple_dots():
#     result = parse_price("1.000.99")
#     assert result == 1000.99
#
#
# def test_parse_price_invalid_format():
#     with pytest.raises(ValueError, match="Invalid format for float conversion"):
#         parse_price("abc")
