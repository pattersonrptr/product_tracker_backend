from datetime import datetime, timezone

from src.app.infrastructure.repositories.price_history_repository import (
    PriceHistoryRepository,
)
from src.app.entities import price_history as PriceHistoryEntity
from src.app.infrastructure.database.models import (
    price_history_model as PriceHistoryModel,
)


def test_create_price_history(mocker):
    mock_db = mocker.MagicMock()
    repo = PriceHistoryRepository(mock_db)
    price_history_entity = PriceHistoryEntity.PriceHistory(product_id=1, price=10.50)

    created_entity = repo.create(price_history_entity)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    assert created_entity.product_id == price_history_entity.product_id
    assert created_entity.price == price_history_entity.price
    assert isinstance(created_entity.created_at, datetime)


def test_get_by_product_id(mocker):
    mock_db = mocker.MagicMock()
    repo = PriceHistoryRepository(mock_db)
    mock_db.query.return_value.filter.return_value.all.return_value = [
        PriceHistoryModel.PriceHistory(
            id=1, product_id=1, price=10.50, created_at=datetime.now(timezone.utc)
        ),
        PriceHistoryModel.PriceHistory(
            id=2, product_id=1, price=12.00, created_at=datetime.now(timezone.utc)
        ),
    ]

    history = repo.get_by_product_id(1)

    mock_db.query.assert_called_once_with(PriceHistoryModel.PriceHistory)
    mock_db.query.return_value.filter.assert_called_once()
    mock_db.query.return_value.filter.return_value.all.assert_called_once()

    assert len(history) == 2
    assert all(isinstance(item, PriceHistoryEntity.PriceHistory) for item in history)
    assert history[0].product_id == 1
    assert history[0].price == 10.50
    assert history[1].product_id == 1
    assert history[1].price == 12.00


def test_get_latest_price(mocker):
    mock_db = mocker.MagicMock()
    repo = PriceHistoryRepository(mock_db)
    now = datetime.now(timezone.utc)
    mock_price_history_model = PriceHistoryModel.PriceHistory(
        id=3, product_id=1, price=15.00, created_at=now
    )
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_price_history_model

    latest_price = repo.get_latest_price(1)

    mock_db.query.assert_called_once_with(PriceHistoryModel.PriceHistory)
    mock_db.query.return_value.filter.assert_called_once()
    mock_db.query.return_value.filter.return_value.order_by.assert_called_once()
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.assert_called_once()

    assert latest_price is not None
    assert isinstance(latest_price, PriceHistoryEntity.PriceHistory)
    assert latest_price.product_id == 1
    assert latest_price.price == 15.00
    assert latest_price.created_at == now


def test_get_latest_price_no_history(mocker):
    mock_db = mocker.MagicMock()
    repo = PriceHistoryRepository(mock_db)
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_order_by = mock_filter.order_by.return_value
    mock_order_by.first.return_value = None

    latest_price = repo.get_latest_price(999)

    mock_db.query.assert_called_once_with(PriceHistoryModel.PriceHistory)
    mock_query.filter.assert_called_once()
    mock_filter.order_by.assert_called_once()
    mock_order_by.first.assert_called_once()

    assert latest_price is None
