from datetime import datetime, UTC

from app.infrastructure.repositories.price_history_repository import (
    PriceHistoryRepository,
)
from app.entities import price_history as PriceHistoryEntity
from app.infrastructure.database.models import price_history_model as PriceHistoryModel


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
    mock_db.query().filter().all.return_value = [
        PriceHistoryModel(
            id=1, product_id=1, price=10.50, created_at=datetime.now(UTC)
        ),
        PriceHistoryModel(
            id=2, product_id=1, price=12.00, created_at=datetime.now(UTC)
        ),
    ]

    history = repo.get_by_product_id(1)

    mock_db.query.assert_called_once()
    mock_db.query().filter.assert_called_once_with(PriceHistoryModel.product_id == 1)
    mock_db.query().filter().all.assert_called_once()
    assert len(history) == 2
    assert all(isinstance(item, PriceHistoryEntity.PriceHistory) for item in history)
    assert history[0].product_id == 1
    assert history[1].price == 12.00


def test_get_latest_price(mocker):
    mock_db = mocker.MagicMock()
    repo = PriceHistoryRepository(mock_db)
    now = datetime.now(UTC)
    mock_db.query().filter().order_by().first.return_value = PriceHistoryModel(
        id=3, product_id=1, price=15.00, created_at=now
    )

    latest_price = repo.get_latest_price(1)

    mock_db.query.assert_called_once()
    mock_db.query().filter.assert_called_once_with(PriceHistoryModel.product_id == 1)
    mock_db.query().filter().order_by.assert_called_once()
    mock_db.query().filter().order_by().first.assert_called_once()
    assert latest_price is not None
    assert isinstance(latest_price, PriceHistoryEntity.PriceHistory)
    assert latest_price.product_id == 1
    assert latest_price.price == 15.00


def test_get_latest_price_no_history(mocker):
    mock_db = mocker.MagicMock()
    repo = PriceHistoryRepository(mock_db)
    mock_db.query().filter().order_by().first.return_value = None

    latest_price = repo.get_latest_price(1)

    assert latest_price is None
