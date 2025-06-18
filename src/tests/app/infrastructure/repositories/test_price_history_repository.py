from datetime import datetime, timezone

import pytest

from src.app.infrastructure.repositories.price_history_repository import (
    PriceHistoryRepository,
)
from src.app.entities import price_history as PriceHistoryEntity
from src.app.infrastructure.database.models import (
    price_history_model as PriceHistoryModel,
)


@pytest.fixture
def mock_db(mocker):
    return mocker.MagicMock()


@pytest.fixture
def repo(mock_db):
    return PriceHistoryRepository(mock_db)


def test_create_price_history_success(repo, mock_db):
    price_history_entity = PriceHistoryEntity.PriceHistory(product_id=1, price=10.50)
    created_entity = repo.create(price_history_entity)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    assert created_entity.product_id == price_history_entity.product_id
    assert created_entity.price == price_history_entity.price
    assert isinstance(created_entity.created_at, datetime)


def test_create_price_history_exception(repo, mock_db, mocker):
    price_history_entity = PriceHistoryEntity.PriceHistory(product_id=1, price=10.50)
    mock_db.add.side_effect = Exception("fail")
    mock_db.rollback = mocker.MagicMock()
    with pytest.raises(Exception):
        repo.create(price_history_entity)
    mock_db.rollback.assert_called_once()


def test_get_by_product_id_found(repo, mock_db):
    now = datetime.now(timezone.utc)
    mock_db.query.return_value.filter.return_value.all.return_value = [
        PriceHistoryModel.PriceHistory(id=1, product_id=1, price=10.50, created_at=now),
        PriceHistoryModel.PriceHistory(id=2, product_id=1, price=12.00, created_at=now),
    ]
    history = repo.get_by_product_id(1)
    assert len(history) == 2
    assert all(isinstance(item, PriceHistoryEntity.PriceHistory) for item in history)
    assert history[0].product_id == 1
    assert history[1].price == 12.00


def test_get_by_product_id_empty(repo, mock_db):
    mock_db.query.return_value.filter.return_value.all.return_value = []
    history = repo.get_by_product_id(999)
    assert history == []


def test_get_latest_price_found(repo, mock_db):
    now = datetime.now(timezone.utc)
    mock_price_history_model = PriceHistoryModel.PriceHistory(
        id=3, product_id=1, price=15.00, created_at=now
    )
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_price_history_model
    latest_price = repo.get_latest_price(1)
    assert latest_price is not None
    assert isinstance(latest_price, PriceHistoryEntity.PriceHistory)
    assert latest_price.product_id == 1
    assert latest_price.price == 15.00
    assert latest_price.created_at == now


def test_get_latest_price_none(repo, mock_db):
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
    latest_price = repo.get_latest_price(999)
    assert latest_price is None


def test_create_and_get_by_product_id_integration(mocker):
    # Integração simulada: cria e busca
    mock_db = mocker.MagicMock()
    repo = PriceHistoryRepository(mock_db)
    entity = PriceHistoryEntity.PriceHistory(product_id=2, price=20.0)
    # Simula create
    repo.create(entity)
    mock_db.add.assert_called_once()
    # Simula get_by_product_id
    now = datetime.now(timezone.utc)
    mock_db.query.return_value.filter.return_value.all.return_value = [
        PriceHistoryModel.PriceHistory(id=10, product_id=2, price=20.0, created_at=now)
    ]
    result = repo.get_by_product_id(2)
    assert len(result) == 1
    assert result[0].product_id == 2
    assert result[0].price == 20.0


def test_create_rollback_on_commit_exception(repo, mock_db, mocker):
    price_history_entity = PriceHistoryEntity.PriceHistory(product_id=3, price=30.0)
    mock_db.commit.side_effect = Exception("commit fail")
    mock_db.rollback = mocker.MagicMock()
    with pytest.raises(Exception):
        repo.create(price_history_entity)
    mock_db.rollback.assert_called_once()


def test_create_rollback_on_refresh_exception(repo, mock_db, mocker):
    price_history_entity = PriceHistoryEntity.PriceHistory(product_id=4, price=40.0)
    mock_db.refresh.side_effect = Exception("refresh fail")
    mock_db.rollback = mocker.MagicMock()
    with pytest.raises(Exception):
        repo.create(price_history_entity)
    mock_db.rollback.assert_called_once()


def test_get_by_product_id_with_extra_attrs(repo, mock_db):
    now = datetime.now(timezone.utc)

    # Simula um modelo com atributos extras
    class DummyModel:
        def __init__(self):
            self.id = 99
            self.product_id = 42
            self.price = 99.99
            self.created_at = now
            self.extra = "should be ignored"

        def __dict__(self):
            # Simula __dict__ como dicionário real
            return {
                "id": self.id,
                "product_id": self.product_id,
                "price": self.price,
                "created_at": self.created_at,
                "extra": self.extra,
            }

    dummy = DummyModel()
    # Força __dict__ como atributo, não método
    dummy.__dict__ = {
        "id": dummy.id,
        "product_id": dummy.product_id,
        "price": dummy.price,
        "created_at": dummy.created_at,
        "extra": dummy.extra,
    }
    mock_db.query.return_value.filter.return_value.all.return_value = [dummy]
    result = repo.get_by_product_id(42)
    assert result[0].product_id == 42
    assert hasattr(result[0], "price")
    assert not hasattr(result[0], "extra")


def test_get_by_product_id_model_to_entity_exception(repo, mock_db, monkeypatch):
    # Simula erro ao criar entidade a partir do modelo
    class DummyModel:
        @property
        def __dict__(self):
            raise ValueError("dict error")

    mock_db.query.return_value.filter.return_value.all.return_value = [DummyModel()]
    with pytest.raises(ValueError):
        repo.get_by_product_id(1)


def test_get_by_product_id_db_exception(repo, mock_db):
    mock_db.query.side_effect = Exception("db fail")
    with pytest.raises(Exception):
        repo.get_by_product_id(1)


def test_get_latest_price_db_exception(repo, mock_db):
    mock_db.query.side_effect = Exception("db fail")
    with pytest.raises(Exception):
        repo.get_latest_price(1)
