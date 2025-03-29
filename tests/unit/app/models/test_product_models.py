from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric, String

from app.models.product_models import Product


def test_product_table_name():
    assert Product.__tablename__ == "product"


def test_id_column():
    col = Product.__table__.c.id
    assert isinstance(col.type, Integer)
    assert col.primary_key
    assert not col.nullable


def test_url_column():
    col = Product.__table__.c.url
    assert isinstance(col.type, String)
    assert col.unique
    assert col.nullable


def test_title_column():
    col = Product.__table__.c.title
    assert isinstance(col.type, String)
    assert col.nullable


def test_price_column():
    col = Product.__table__.c.price
    assert isinstance(col.type, Numeric)
    assert col.type.precision == 10
    assert col.type.scale == 2
    assert col.nullable


def test_created_at_column():
    col = Product.__table__.c.created_at
    assert isinstance(col.type, DateTime)
    assert not col.nullable
    assert col.default is not None


def test_created_at_default_value():
    created_at_column = Product.__table__.c.created_at

    assert created_at_column.default is not None

    default_value = created_at_column.default
    if default_value.is_callable:

        class FakeContext:
            def __init__(self):
                self.current_parameters = {}

        ctx = FakeContext()
        generated_value = default_value.arg(ctx)
    else:
        generated_value = default_value.arg

    assert isinstance(generated_value, datetime)
    assert generated_value.tzinfo is not None
