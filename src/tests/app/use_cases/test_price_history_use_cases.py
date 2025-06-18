from unittest.mock import MagicMock
from datetime import datetime, timezone

from src.app.entities.price_history import PriceHistory as PriceHistoryEntity
from src.app.use_cases.price_history_use_cases import (
    CreatePriceHistoryUseCase,
    GetLatestPriceUseCase,
)
from src.app.use_cases.price_history_use_cases import GetPriceHistoryByProductIdUseCase


def test_create_price_history_use_case_success():
    price_history_repo_mock = MagicMock()
    price_history_input = PriceHistoryEntity(
        product_id=1,
        price=99.99,
    )

    mock_created_price_history_entity = PriceHistoryEntity(
        id=1,
        product_id=price_history_input.product_id,
        price=price_history_input.price,
        created_at=datetime.now(timezone.utc),
    )
    price_history_repo_mock.create.return_value = mock_created_price_history_entity
    use_case = CreatePriceHistoryUseCase(price_history_repo_mock)
    result = use_case.execute(price_history_input)
    price_history_repo_mock.create.assert_called_once_with(price_history_input)
    assert result == mock_created_price_history_entity


def test_get_price_history_by_product_id_use_case_success():
    price_history_repo_mock = MagicMock()
    product_id_to_search = 123
    mock_price_histories = [
        PriceHistoryEntity(
            id=1,
            product_id=product_id_to_search,
            price=100.00,
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        ),
        PriceHistoryEntity(
            id=2,
            product_id=product_id_to_search,
            price=95.50,
            created_at=datetime(2023, 1, 5, tzinfo=timezone.utc),
        ),
    ]
    price_history_repo_mock.get_by_product_id.return_value = mock_price_histories
    use_case = GetPriceHistoryByProductIdUseCase(price_history_repo_mock)
    result = use_case.execute(product_id_to_search)
    price_history_repo_mock.get_by_product_id.assert_called_once_with(
        product_id_to_search
    )
    assert result == mock_price_histories
    assert len(result) == 2


def test_get_latest_price_use_case_success():
    price_history_repo_mock = MagicMock()
    product_id_to_search = 456
    mock_latest_price_history = PriceHistoryEntity(
        id=3,
        product_id=product_id_to_search,
        price=150.75,
        created_at=datetime.now(timezone.utc),
    )
    price_history_repo_mock.get_latest_price.return_value = mock_latest_price_history
    use_case = GetLatestPriceUseCase(price_history_repo_mock)
    result = use_case.execute(product_id_to_search)
    price_history_repo_mock.get_latest_price.assert_called_once_with(
        product_id_to_search
    )
    assert result == mock_latest_price_history


def test_get_latest_price_use_case_no_price_found():
    price_history_repo_mock = MagicMock()
    product_id_to_search = 789
    price_history_repo_mock.get_latest_price.return_value = None
    use_case = GetLatestPriceUseCase(price_history_repo_mock)
    result = use_case.execute(product_id_to_search)
    price_history_repo_mock.get_latest_price.assert_called_once_with(
        product_id_to_search
    )
    assert result is None
