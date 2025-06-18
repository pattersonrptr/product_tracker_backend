from datetime import datetime, timezone

from src.app.entities.product import Product


def test_product_minimal_fields():
    product = Product(url="http://example.com", title="Produto", source_website_id=1)
    assert product.url == "http://example.com"
    assert product.title == "Produto"
    assert product.source_website_id == 1
    assert product.is_available is True
    assert isinstance(product.created_at, datetime)
    assert isinstance(product.updated_at, datetime)


def test_product_all_fields():
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    product = Product(
        url="http://example.com",
        title="Produto",
        source_website_id=2,
        description="desc",
        source_product_code="SRC123",
        city="Cidade",
        state="UF",
        condition="NEW",
        seller_name="Vendedor",
        is_available=False,
        image_urls="img.jpg",
        source_metadata={"foo": "bar"},
        created_at=now,
        updated_at=now,
        current_price=99.99,
        id=10,
    )
    assert product.description == "desc"
    assert product.source_product_code == "SRC123"
    assert product.city == "Cidade"
    assert product.state == "UF"
    assert product.condition == "NEW"
    assert product.seller_name == "Vendedor"
    assert product.is_available is False
    assert product.image_urls == "img.jpg"
    assert product.source_metadata == {"foo": "bar"}
    assert product.created_at == now
    assert product.updated_at == now
    assert product.current_price == 99.99
    assert product.id == 10


def test_product_defaults_are_independent():
    p1 = Product(url="a", title="b", source_website_id=1)
    p2 = Product(url="c", title="d", source_website_id=2)
    assert p1.created_at != p2.created_at or p1.updated_at != p2.updated_at
