from decimal import Decimal
from datetime import datetime

from src.app.interfaces.schemas.price_history_schema import (
    PriceHistoryBase, PriceHistoryCreate, PriceHistoryRead, PriceHistoryUpdate
)

def test_price_history_base():
    obj = PriceHistoryBase(product_id=1, price=Decimal("10.50"))
    assert obj.product_id == 1
    assert obj.price == Decimal("10.50")

def test_price_history_create():
    obj = PriceHistoryCreate(product_id=2, price=Decimal("20.00"))
    assert obj.product_id == 2

def test_price_history_read():
    now = datetime.utcnow()
    obj = PriceHistoryRead(id=1, product_id=3, price=Decimal("30.00"), created_at=now)
    assert obj.id == 1
    assert obj.created_at == now

def test_price_history_update():
    now = datetime.utcnow()
    obj = PriceHistoryUpdate(id=2, product_id=4, price=Decimal("40.00"), created_at=now)
    assert obj.id == 2
    assert obj.created_at == now
