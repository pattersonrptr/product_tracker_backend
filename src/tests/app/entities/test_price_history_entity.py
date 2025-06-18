from datetime import datetime, timezone
from src.app.entities.price_history import PriceHistory


def test_price_history_minimal_fields():
    ph = PriceHistory(product_id=1, price=10.5)
    assert ph.product_id == 1
    assert ph.price == 10.5
    assert isinstance(ph.created_at, datetime)
    assert ph.id is None


def test_price_history_all_fields():
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    ph = PriceHistory(product_id=2, price=20.0, created_at=now, id=5)
    assert ph.product_id == 2
    assert ph.price == 20.0
    assert ph.created_at == now
    assert ph.id == 5
