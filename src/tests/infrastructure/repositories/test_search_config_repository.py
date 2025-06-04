from src.app.infrastructure.repositories.search_config_repository import (
    SearchConfigRepository,
)
from src.app.entities import search_config as SearchConfigEntity
from datetime import datetime, timezone, time
from types import SimpleNamespace
from unittest.mock import MagicMock


def test_create_search_config():
    db_mock = MagicMock()

    repository = SearchConfigRepository(db_mock)

    search_config_entity = SearchConfigEntity.SearchConfig(
        search_term="test create",
        is_active=True,
        frequency_days=7,
        preferred_time=time(10, 0),
        user_id=1,
        search_metadata={"key": "value"},
    )

    mock_db_model = SimpleNamespace(
        id=1,
        search_term="test create",
        is_active=True,
        frequency_days=7,
        preferred_time=time(10, 0),
        search_metadata={"key": "value"},
        user_id=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        source_websites=[],
    )

    mock_db_model = SimpleNamespace(
        id=1,
        search_term="test create",
        is_active=True,
        frequency_days=7,
        preferred_time=time(10, 0),
        search_metadata={"key": "value"},
        user_id=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        source_websites=[],
    )

    db_mock.add.return_value = None

    db_mock.refresh.side_effect = lambda obj: setattr(
        obj, "__dict__", mock_db_model.__dict__
    )
    db_mock.commit.return_value = None

    result = repository.create(search_config_entity)

    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()

    assert result.id == 1
    assert result.search_term == "test create"
    assert result.is_active is True
    assert result.frequency_days == 7
    assert result.preferred_time == time(10, 0)
    assert result.user_id == 1
    assert result.search_metadata == {"key": "value"}


def test_get_by_id_search_config():
    db_mock = MagicMock()
    repository = SearchConfigRepository(db_mock)

    mock_db_model = SimpleNamespace(
        id=1,
        search_term="test get by id",
        is_active=True,
        frequency_days=1,
        preferred_time=time(12, 0),
        search_metadata={"source": "mock"},
        user_id=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        source_websites=[
            SimpleNamespace(
                id=101,
                name="Website A",
                base_url="http://websitea.com",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                products=[],
            )
        ],
    )

    db_mock.query.return_value.options.return_value.options.return_value.options.return_value.filter.return_value.first.return_value = mock_db_model

    result = repository.get_by_id(1)

    assert result is not None
    assert result.id == 1
    assert result.search_term == "test get by id"
    assert len(result.source_websites) == 1
    assert result.source_websites[0].name == "Website A"

    db_mock.query.return_value.options.return_value.options.return_value.options.return_value.filter.return_value.first.return_value = None
    result = repository.get_by_id(999)
    assert result is None


def test_get_all_search_configs_no_filters():
    db_mock = MagicMock()
    repository = SearchConfigRepository(db_mock)

    mock_db_models = [
        SimpleNamespace(
            id=1,
            search_term="Test 1",
            is_active=True,
            frequency_days=1,
            preferred_time=time(10, 0),
            search_metadata={"key": "value1"},
            user_id=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=2,
            search_term="Test 2",
            is_active=False,
            frequency_days=7,
            preferred_time=time(14, 0),
            search_metadata={"key": "value2"},
            user_id=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            source_websites=[],
        ),
    ]

    mock_query_obj = MagicMock()

    mock_query_obj.options.return_value = mock_query_obj

    mock_query_obj.filter.return_value = mock_query_obj
    mock_query_obj.order_by.return_value = mock_query_obj
    mock_query_obj.offset.return_value = mock_query_obj
    mock_query_obj.limit.return_value = mock_query_obj

    mock_query_obj.all.return_value = mock_db_models
    mock_query_obj.count.return_value = len(mock_db_models)

    db_mock.query.return_value = mock_query_obj

    search_configs, total_count = repository.get_all()

    assert len(search_configs) == 2
    assert total_count == 2
    assert search_configs[0].search_term == "Test 1"
    assert search_configs[1].search_term == "Test 2"

    db_mock.query.assert_called_once()

    assert mock_query_obj.options.call_count == 3

    mock_query_obj.count.assert_called_once()

    mock_query_obj.limit.assert_called_once_with(10)

    mock_query_obj.offset.assert_called_once_with(0)

    mock_query_obj.all.assert_called_once()

    mock_query_obj.filter.assert_not_called()
    mock_query_obj.order_by.assert_not_called()


def test_get_all_search_configs_with_filters():
    db_mock = MagicMock()
    repository = SearchConfigRepository(db_mock)

    mock_db_models = [
        SimpleNamespace(
            id=1,
            search_term="Laptop",
            is_active=True,
            frequency_days=1,
            preferred_time=time(9, 0),
            search_metadata={"category": "electronics"},
            user_id=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=2,
            search_term="Smartphone",
            is_active=False,
            frequency_days=3,
            preferred_time=time(14, 30),
            search_metadata={"category": "electronics"},
            user_id=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=3,
            search_term="Monitor",
            is_active=True,
            frequency_days=7,
            preferred_time=time(8, 0),
            search_metadata={"category": "peripherals"},
            user_id=2,
            created_at=datetime(2023, 1, 3, 12, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 3, 12, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
    ]

    mock_query_obj = MagicMock()

    mock_query_obj.options.return_value = mock_query_obj

    mock_query_obj.filter.return_value = mock_query_obj
    mock_query_obj.order_by.return_value = mock_query_obj
    mock_query_obj.offset.return_value = mock_query_obj
    mock_query_obj.limit.return_value = mock_query_obj

    filtered_models = [mock_db_models[0]]
    mock_query_obj.all.return_value = filtered_models
    mock_query_obj.count.return_value = len(filtered_models)

    db_mock.query.return_value = mock_query_obj

    filter_data = {"search_term": {"value": "Laptop", "operator": "equals"}}
    search_configs, total_count = repository.get_all(
        column_filters=filter_data, limit=10, offset=0
    )

    assert len(search_configs) == 1
    assert total_count == 1
    assert search_configs[0].search_term == "Laptop"

    db_mock.query.assert_called_once()
    assert mock_query_obj.options.call_count == 3
    assert mock_query_obj.filter.call_count == len(filter_data)
    mock_query_obj.count.assert_called_once()
    mock_query_obj.limit.assert_called_once_with(10)
    mock_query_obj.offset.assert_called_once_with(0)
    mock_query_obj.all.assert_called_once()
    mock_query_obj.order_by.assert_not_called()


def test_get_all_search_configs_with_sorting():
    db_mock = MagicMock()
    repository = SearchConfigRepository(db_mock)

    mock_db_models = [
        SimpleNamespace(
            id=1,
            search_term="Banana",
            is_active=True,
            frequency_days=5,
            preferred_time=time(10, 0),
            search_metadata={},
            user_id=1,
            created_at=datetime(2023, 1, 5, 10, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 5, 10, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=2,
            search_term="Apple",
            is_active=False,
            frequency_days=2,
            preferred_time=time(14, 0),
            search_metadata={},
            user_id=1,
            created_at=datetime(2023, 1, 2, 11, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 2, 11, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=3,
            search_term="Cherry",
            is_active=True,
            frequency_days=1,
            preferred_time=time(8, 0),
            search_metadata={},
            user_id=2,
            created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
    ]

    mock_query_obj = MagicMock()

    mock_query_obj.options.return_value = mock_query_obj

    mock_query_obj.filter.return_value = mock_query_obj
    mock_query_obj.order_by.return_value = mock_query_obj
    mock_query_obj.offset.return_value = mock_query_obj
    mock_query_obj.limit.return_value = mock_query_obj

    sorted_models_asc = [
        mock_db_models[1],
        mock_db_models[0],
        mock_db_models[2],
    ]
    mock_query_obj.all.return_value = sorted_models_asc
    mock_query_obj.count.return_value = len(mock_db_models)

    db_mock.query.return_value = mock_query_obj

    search_configs, total_count = repository.get_all(
        sort_by="search_term", sort_order="asc", limit=10, offset=0
    )

    assert len(search_configs) == 3
    assert total_count == 3
    assert search_configs[0].search_term == "Apple"
    assert search_configs[1].search_term == "Banana"
    assert search_configs[2].search_term == "Cherry"

    db_mock.query.assert_called_once()
    assert mock_query_obj.options.call_count == 3
    mock_query_obj.order_by.assert_called_once()
    mock_query_obj.count.assert_called_once()
    mock_query_obj.limit.assert_called_once_with(10)
    mock_query_obj.offset.assert_called_once_with(0)
    mock_query_obj.all.assert_called_once()
    mock_query_obj.filter.assert_not_called()

    db_mock.reset_mock()

    mock_query_obj = MagicMock()
    mock_query_obj.options.return_value = mock_query_obj
    mock_query_obj.filter.return_value = mock_query_obj
    mock_query_obj.order_by.return_value = mock_query_obj
    mock_query_obj.offset.return_value = mock_query_obj
    mock_query_obj.limit.return_value = mock_query_obj

    sorted_models_desc = [
        mock_db_models[2],
        mock_db_models[0],
        mock_db_models[1],
    ]
    mock_query_obj.all.return_value = sorted_models_desc
    mock_query_obj.count.return_value = len(mock_db_models)
    db_mock.query.return_value = mock_query_obj

    search_configs_desc, total_count_desc = repository.get_all(
        sort_by="search_term", sort_order="desc", limit=10, offset=0
    )

    assert len(search_configs_desc) == 3
    assert total_count_desc == 3
    assert search_configs_desc[0].search_term == "Cherry"
    assert search_configs_desc[1].search_term == "Banana"
    assert search_configs_desc[2].search_term == "Apple"

    db_mock.query.assert_called_once()
    assert mock_query_obj.options.call_count == 3
    mock_query_obj.order_by.assert_called_once()
    mock_query_obj.count.assert_called_once()
    mock_query_obj.limit.assert_called_once_with(10)
    mock_query_obj.offset.assert_called_once_with(0)
    mock_query_obj.all.assert_called_once()
    mock_query_obj.filter.assert_not_called()


def test_get_all_search_configs_with_filters_and_sorting():
    db_mock = MagicMock()
    repository = SearchConfigRepository(db_mock)

    mock_db_models = [
        SimpleNamespace(
            id=1,
            search_term="Monitor 27 inch",
            is_active=True,
            frequency_days=7,
            preferred_time=time(10, 0),
            search_metadata={"type": "electronics"},
            user_id=1,
            created_at=datetime(2023, 1, 10, 10, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 10, 10, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=2,
            search_term="Smart TV 55 inch",
            is_active=True,
            frequency_days=1,
            preferred_time=time(14, 0),
            search_metadata={"type": "electronics"},
            user_id=2,
            created_at=datetime(2023, 1, 12, 14, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 12, 14, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=3,
            search_term="Laptop Gamer",
            is_active=False,
            frequency_days=3,
            preferred_time=time(8, 0),
            search_metadata={"type": "electronics"},
            user_id=1,
            created_at=datetime(2023, 1, 11, 8, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 11, 8, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=4,
            search_term="Keyboard Mechanical",
            is_active=True,
            frequency_days=7,
            preferred_time=time(16, 0),
            search_metadata={"type": "peripherals"},
            user_id=2,
            created_at=datetime(2023, 1, 9, 16, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 9, 16, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
    ]

    mock_query_obj = MagicMock()

    mock_query_obj.options.return_value = mock_query_obj

    mock_query_obj.filter.return_value = mock_query_obj
    mock_query_obj.order_by.return_value = mock_query_obj
    mock_query_obj.offset.return_value = mock_query_obj
    mock_query_obj.limit.return_value = mock_query_obj

    filtered_and_sorted_models = [
        mock_db_models[0],
        mock_db_models[1],
    ]

    mock_query_obj.all.return_value = filtered_and_sorted_models
    mock_query_obj.count.return_value = len(filtered_and_sorted_models)

    db_mock.query.return_value = mock_query_obj

    filter_data = {
        "is_active": {"value": True, "operator": "equals"},
        "search_term": {"value": "inch", "operator": "contains"},
    }
    search_configs, total_count = repository.get_all(
        column_filters=filter_data,
        sort_by="search_term",
        sort_order="asc",
        limit=10,
        offset=0,
    )

    assert len(search_configs) == 2
    assert total_count == 2
    assert search_configs[0].search_term == "Monitor 27 inch"
    assert search_configs[1].search_term == "Smart TV 55 inch"

    db_mock.query.assert_called_once()
    assert mock_query_obj.options.call_count == 3
    assert mock_query_obj.filter.call_count == len(filter_data)
    mock_query_obj.order_by.assert_called_once()
    mock_query_obj.count.assert_called_once()
    mock_query_obj.limit.assert_called_once_with(10)
    mock_query_obj.offset.assert_called_once_with(0)
    mock_query_obj.all.assert_called_once()

    db_mock.reset_mock()

    filtered_and_sorted_models_2 = [
        SimpleNamespace(
            id=4,
            search_term="Keyboard Mechanical",
            is_active=True,
            frequency_days=7,
            preferred_time=time(16, 0),
            search_metadata={"type": "peripherals"},
            user_id=2,
            created_at=datetime(2023, 1, 9, 16, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 15, 16, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=2,
            search_term="Smart TV 55 inch",
            is_active=True,
            frequency_days=1,
            preferred_time=time(14, 0),
            search_metadata={"type": "electronics"},
            user_id=2,
            created_at=datetime(2023, 1, 12, 14, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 12, 14, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
    ]

    mock_query_obj_2 = MagicMock()
    mock_query_obj_2.options.return_value = mock_query_obj_2
    mock_query_obj_2.filter.return_value = mock_query_obj_2
    mock_query_obj_2.order_by.return_value = mock_query_obj_2
    mock_query_obj_2.offset.return_value = mock_query_obj_2
    mock_query_obj_2.limit.return_value = mock_query_obj_2
    mock_query_obj_2.all.return_value = filtered_and_sorted_models_2
    mock_query_obj_2.count.return_value = len(filtered_and_sorted_models_2)
    db_mock.query.return_value = mock_query_obj_2

    filter_data_2 = {
        "user_id": {"value": 2, "operator": "equals"},
    }
    search_configs_2, total_count_2 = repository.get_all(
        column_filters=filter_data_2,
        sort_by="updated_at",
        sort_order="desc",
        limit=10,
        offset=0,
    )

    assert len(search_configs_2) == 2
    assert total_count_2 == 2
    assert search_configs_2[0].search_term == "Keyboard Mechanical"
    assert search_configs_2[1].search_term == "Smart TV 55 inch"

    db_mock.query.assert_called_once()
    assert mock_query_obj_2.options.call_count == 3
    assert mock_query_obj_2.filter.call_count == len(filter_data_2)
    mock_query_obj_2.order_by.assert_called_once()
    mock_query_obj_2.count.assert_called_once()
    mock_query_obj_2.limit.assert_called_once_with(10)
    mock_query_obj_2.offset.assert_called_once_with(0)
    mock_query_obj_2.all.assert_called_once()


def test_update_search_config_basic_fields():
    db_mock = MagicMock()
    repository = SearchConfigRepository(db_mock)

    existing_db_model = SimpleNamespace(
        id=1,
        search_term="Old Term",
        is_active=True,
        frequency_days=7,
        preferred_time=time(9, 0),
        search_metadata={"initial": "value"},
        user_id=1,
        created_at=datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        source_websites=[],
    )

    db_mock.query.return_value.filter.return_value.first.return_value = (
        existing_db_model
    )

    mock_get_by_id_result = SimpleNamespace(
        id=1,
        search_term="New Term",
        is_active=False,
        frequency_days=3,
        preferred_time=time(15, 30),
        search_metadata={"updated": "value"},
        user_id=1,
        created_at=datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime.now(timezone.utc),
        source_websites=[],
    )

    repository.get_by_id = MagicMock(
        return_value=SearchConfigEntity.SearchConfig(
            id=mock_get_by_id_result.id,
            search_term=mock_get_by_id_result.search_term,
            is_active=mock_get_by_id_result.is_active,
            frequency_days=mock_get_by_id_result.frequency_days,
            preferred_time=mock_get_by_id_result.preferred_time,
            search_metadata=mock_get_by_id_result.search_metadata,
            user_id=mock_get_by_id_result.user_id,
            created_at=mock_get_by_id_result.created_at,
            updated_at=mock_get_by_id_result.updated_at,
            source_websites=[],
        )
    )

    update_entity = SearchConfigEntity.SearchConfig(
        search_term="New Term",
        is_active=False,
        frequency_days=3,
        preferred_time=time(15, 30),
        user_id=1,
        search_metadata={"updated": "value"},
    )

    result = repository.update(1, update_entity)

    assert result is not None
    assert result.id == 1
    assert result.search_term == "New Term"
    assert result.is_active is False
    assert result.frequency_days == 3
    assert result.preferred_time == time(15, 30)
    assert result.search_metadata == {"updated": "value"}
    assert result.user_id == 1

    db_mock.query.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(existing_db_model)
    repository.get_by_id.assert_called_once_with(1)


def test_update_search_config_not_found():
    db_mock = MagicMock()
    repository = SearchConfigRepository(db_mock)

    db_mock.query.return_value.filter.return_value.first.return_value = None

    update_entity = SearchConfigEntity.SearchConfig(
        search_term="Non Existent",
        is_active=True,
        frequency_days=1,
        preferred_time=time(10, 0),
        user_id=1,
    )

    result = repository.update(999, update_entity)

    assert result is None
    db_mock.query.assert_called_once()
    db_mock.commit.assert_not_called()
    db_mock.refresh.assert_not_called()
