import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.product_schema import (
    ProductBase,
    ProductCreate,
    ProductResponse
)


@pytest.fixture
def valid_product_data():
    return {
        "url": "https://olx.com/item/123",
        "title": "Smartphone XYZ",
        "price": 1500.90
    }


@pytest.fixture
def valid_response_data(valid_product_data):
    return {
        **valid_product_data,
        "id": 1,
        "created_at": datetime.now()
    }


class TestProductSchema:
    def test_base_schema_valid_data(self, valid_product_data):
        product = ProductBase(**valid_product_data)
        assert str(product.url) == valid_product_data["url"]
        assert product.title == valid_product_data["title"]
        assert product.price == valid_product_data["price"]

    def test_create_schema_inheritance(self, valid_product_data):
        product_create = ProductCreate(**valid_product_data)
        assert isinstance(product_create, ProductBase)

    def test_response_schema_with_orm_mode(self, valid_response_data):
        product = ProductResponse(**valid_response_data)
        assert product.id == valid_response_data["id"]
        assert product.created_at == valid_response_data["created_at"]

    @pytest.mark.parametrize("invalid_data, expected_error", [
        ({"title": "Teste", "price": 100}, "url\n  Field required"),

        (
                {"url": 123, "title": "Teste", "price": 100},
                "url\n  URL input should be a string or URL"
        ),
        (
                {"url": "teste", "title": "Teste", "price": "cem"},
                "price\n  Input should be a valid number"
        ),

        (
                {"url": "invalid_url", "title": "", "price": -50},
                [
                    "url\n  Input should be a valid URL, relative URL without a base",
                    "title\n  String should have at least 1 character",
                    "price\n  Input should be greater than 0"
                ]
        )
    ])
    def test_invalid_data_raises_errors(self, invalid_data, expected_error):
        with pytest.raises(ValidationError) as exc_info:
            ProductBase(**invalid_data)

        errors = str(exc_info.value)
        if isinstance(expected_error, list):
            for error in expected_error:
                assert error in errors
        else:
            assert expected_error in errors

    def test_response_schema_requires_extra_fields(self, valid_product_data):
        with pytest.raises(ValidationError) as exc_info:
            ProductResponse(**valid_product_data)

        assert "id\n  Field required" in str(exc_info.value)
        assert "created_at\n  Field required" in str(exc_info.value)
