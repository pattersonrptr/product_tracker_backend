import pytest
from unittest.mock import MagicMock
from datetime import datetime, time, timezone

from src.app.use_cases.search_config_use_cases import (
    CreateSearchConfigUseCase,
    GetSearchConfigUseCase,
    ListSearchConfigsUseCase,
    UpdateSearchConfigUseCase,
    DeleteSearchConfigUseCase,
    GetSearchConfigsByUserUseCase,
    GetSearchConfigsBySourceWebsiteUseCase,
)
from src.app.entities.search_config import SearchConfig as SearchConfigEntity
from src.app.entities.user import User as UserEntity
from src.app.entities.source_website import SourceWebsite as SourceWebsiteEntity
from src.app.use_cases.source_website_use_cases import DeleteSourceWebsiteUseCase


def test_create_search_config_use_case_success():
    search_config_repo_mock = MagicMock()
    user_repo_mock = MagicMock()

    search_config_input = SearchConfigEntity(
        search_term="laptops",
        is_active=True,
        frequency_days=7,
        preferred_time=time(10, 30),
        user_id=1,
    )

    mock_user_entity = UserEntity(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_created_search_config_entity = SearchConfigEntity(
        id=101,
        search_term="laptops",
        is_active=True,
        frequency_days=7,
        preferred_time=time(10, 30),
        user_id=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    user_repo_mock.get_by_id.return_value = mock_user_entity
    search_config_repo_mock.create.return_value = mock_created_search_config_entity
    use_case = CreateSearchConfigUseCase(search_config_repo_mock, user_repo_mock)
    created_search_config = use_case.execute(search_config_input)
    user_repo_mock.get_by_id.assert_called_once_with(search_config_input.user_id)
    search_config_repo_mock.create.assert_called_once_with(search_config_input)
    assert created_search_config == mock_created_search_config_entity


def test_create_search_config_use_case_user_not_found():
    search_config_repo_mock = MagicMock()
    user_repo_mock = MagicMock()
    non_existent_user_id = 999
    search_config_input = SearchConfigEntity(
        search_term="new_gadgets",
        is_active=True,
        frequency_days=1,
        preferred_time=time(14, 0),
        user_id=non_existent_user_id,
    )
    user_repo_mock.get_by_id.return_value = None
    use_case = CreateSearchConfigUseCase(search_config_repo_mock, user_repo_mock)

    with pytest.raises(ValueError) as excinfo:
        use_case.execute(search_config_input)

    user_repo_mock.get_by_id.assert_called_once_with(non_existent_user_id)
    search_config_repo_mock.create.assert_not_called()
    assert f"User with id {non_existent_user_id} not found" in str(excinfo.value)


def test_get_search_config_use_case_success():
    search_config_repo_mock = MagicMock()
    search_config_id = 1
    mock_search_config_entity = SearchConfigEntity(
        id=search_config_id,
        search_term="smartwatch",
        is_active=True,
        frequency_days=3,
        preferred_time=time(9, 0),
        user_id=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    search_config_repo_mock.get_by_id.return_value = mock_search_config_entity
    use_case = GetSearchConfigUseCase(search_config_repo_mock)
    found_search_config = use_case.execute(search_config_id)
    search_config_repo_mock.get_by_id.assert_called_once_with(search_config_id)
    assert found_search_config == mock_search_config_entity


def test_get_search_config_use_case_not_found():
    search_config_repo_mock = MagicMock()
    non_existent_search_config_id = 999
    search_config_repo_mock.get_by_id.return_value = None
    use_case = GetSearchConfigUseCase(search_config_repo_mock)
    found_search_config = use_case.execute(non_existent_search_config_id)
    search_config_repo_mock.get_by_id.assert_called_once_with(
        non_existent_search_config_id
    )
    assert found_search_config is None


def test_list_search_configs_use_case_list_all_success():
    search_config_repo_mock = MagicMock()
    mock_search_configs = [
        SearchConfigEntity(
            id=1,
            search_term="laptops",
            is_active=True,
            frequency_days=7,
            preferred_time=time(10, 30),
            user_id=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        SearchConfigEntity(
            id=2,
            search_term="smartphones",
            is_active=False,
            frequency_days=1,
            preferred_time=time(14, 0),
            user_id=2,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]
    total_count = len(mock_search_configs)
    search_config_repo_mock.get_all.return_value = (mock_search_configs, total_count)
    use_case = ListSearchConfigsUseCase(search_config_repo_mock)
    retrieved_search_configs, count = use_case.execute(
        filter_data={}, limit=10, offset=0
    )
    search_config_repo_mock.get_all.assert_called_once_with(
        column_filters={}, limit=10, offset=0, sort_by=None, sort_order=None
    )
    assert retrieved_search_configs == mock_search_configs
    assert count == total_count


def test_list_search_configs_use_case_with_filters_success():
    search_config_repo_mock = MagicMock()
    filters = {"is_active": True, "user_id": 1}
    mock_filtered_search_configs = [
        SearchConfigEntity(
            id=1,
            search_term="laptops",
            is_active=True,
            frequency_days=7,
            preferred_time=time(10, 30),
            user_id=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    ]
    total_count = len(mock_filtered_search_configs)
    search_config_repo_mock.get_all.return_value = (
        mock_filtered_search_configs,
        total_count,
    )
    use_case = ListSearchConfigsUseCase(search_config_repo_mock)
    retrieved_search_configs, count = use_case.execute(
        filter_data={"column_filters": filters}, limit=10, offset=0
    )

    search_config_repo_mock.get_all.assert_called_once_with(
        column_filters=filters, limit=10, offset=0, sort_by=None, sort_order=None
    )
    assert retrieved_search_configs == mock_filtered_search_configs
    assert count == total_count


def test_list_search_configs_use_case_with_pagination_success():
    search_config_repo_mock = MagicMock()
    all_mock_configs = [
        SearchConfigEntity(
            id=i,
            search_term=f"term_{i}",
            is_active=True,
            frequency_days=1,
            preferred_time=time(10, 0),
            user_id=1,
        )
        for i in range(1, 11)
    ]
    limit = 3
    offset = 3
    expected_configs = all_mock_configs[offset : offset + limit]
    total_count_from_repo = len(all_mock_configs)
    search_config_repo_mock.get_all.return_value = (
        expected_configs,
        total_count_from_repo,
    )
    use_case = ListSearchConfigsUseCase(search_config_repo_mock)
    retrieved_search_configs, count = use_case.execute(
        filter_data={}, limit=limit, offset=offset
    )
    search_config_repo_mock.get_all.assert_called_once_with(
        column_filters={}, limit=limit, offset=offset, sort_by=None, sort_order=None
    )
    assert retrieved_search_configs == expected_configs
    assert count == total_count_from_repo


def test_list_search_configs_use_case_with_sorting_success():
    search_config_repo_mock = MagicMock()
    mock_search_configs_unsorted = [
        SearchConfigEntity(
            id=2,
            search_term="z_term",
            is_active=True,
            frequency_days=7,
            preferred_time=time(10, 30),
            user_id=1,
            created_at=datetime(2023, 1, 2, 10, 30, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 2, 10, 30, tzinfo=timezone.utc),
        ),
        SearchConfigEntity(
            id=1,
            search_term="a_term",
            is_active=True,
            frequency_days=7,
            preferred_time=time(10, 30),
            user_id=1,
            created_at=datetime(2023, 1, 1, 10, 30, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 1, 10, 30, tzinfo=timezone.utc),
        ),
    ]
    mock_search_configs_sorted = sorted(
        mock_search_configs_unsorted, key=lambda x: x.search_term
    )
    total_count = len(mock_search_configs_sorted)
    sort_by = "search_term"
    sort_order = "asc"
    search_config_repo_mock.get_all.return_value = (
        mock_search_configs_sorted,
        total_count,
    )
    use_case = ListSearchConfigsUseCase(search_config_repo_mock)
    retrieved_search_configs, count = use_case.execute(
        filter_data={}, limit=10, offset=0, sort_by=sort_by, sort_order=sort_order
    )
    search_config_repo_mock.get_all.assert_called_once_with(
        column_filters={}, limit=10, offset=0, sort_by=sort_by, sort_order=sort_order
    )
    assert retrieved_search_configs == mock_search_configs_sorted
    assert count == total_count


def test_list_search_configs_use_case_no_search_configs_found():
    search_config_repo_mock = MagicMock()
    search_config_repo_mock.get_all.return_value = ([], 0)
    use_case = ListSearchConfigsUseCase(search_config_repo_mock)
    retrieved_search_configs, count = use_case.execute(
        filter_data={}, limit=10, offset=0
    )
    search_config_repo_mock.get_all.assert_called_once_with(
        column_filters={}, limit=10, offset=0, sort_by=None, sort_order=None
    )
    assert retrieved_search_configs == []
    assert count == 0


def test_update_search_config_use_case_success():
    search_config_repo_mock = MagicMock()
    user_repo_mock = MagicMock()

    search_config_id = 1
    initial_search_term = "old_term"
    updated_search_term = "new_term"

    existing_user_id = 100
    existing_user_entity = UserEntity(
        id=existing_user_id,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    existing_search_config_entity = SearchConfigEntity(
        id=search_config_id,
        search_term=initial_search_term,
        is_active=True,
        frequency_days=1,
        preferred_time=time(9, 0),
        user_id=existing_user_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    updated_search_config_input = SearchConfigEntity(
        search_term=updated_search_term,
        is_active=False,
        frequency_days=5,
        preferred_time=time(15, 0),
        user_id=existing_user_id,
    )

    updated_returned_entity = SearchConfigEntity(
        id=search_config_id,
        search_term=updated_search_term,
        is_active=False,
        frequency_days=5,
        preferred_time=time(15, 0),
        user_id=existing_user_id,
        # created_at=existing_search_config_entity.created_at,
        # updated_at=datetime.now(timezone.utc),
    )

    search_config_repo_mock.get_by_id.return_value = existing_search_config_entity
    search_config_repo_mock.update.return_value = updated_returned_entity
    user_repo_mock.get_by_id.return_value = existing_user_entity

    use_case = UpdateSearchConfigUseCase(search_config_repo_mock, user_repo_mock)

    result = use_case.execute(search_config_id, updated_search_config_input)

    search_config_repo_mock.get_by_id.assert_called_once_with(search_config_id)
    user_repo_mock.get_by_id.assert_called_once_with(existing_user_id)

    args, kwargs = search_config_repo_mock.update.call_args
    called_id = args[0]
    called_entity = args[1]

    assert called_id == search_config_id
    assert called_entity.search_term == updated_search_term
    assert called_entity.is_active is False
    assert called_entity.frequency_days == 5
    assert called_entity.preferred_time == time(15, 0)
    assert called_entity.user_id == existing_user_id
    assert called_entity.id == search_config_id

    assert result == updated_returned_entity


def test_update_search_config_use_case_not_found():
    search_config_repo_mock = MagicMock()
    user_repo_mock = MagicMock()
    non_existent_search_config_id = 999
    update_data = SearchConfigEntity(
        search_term="non_existent_update",
        is_active=False,
        frequency_days=2,
        preferred_time=time(11, 0),
        user_id=1,
    )
    search_config_repo_mock.get_by_id.return_value = None
    use_case = UpdateSearchConfigUseCase(search_config_repo_mock, user_repo_mock)
    result = use_case.execute(non_existent_search_config_id, update_data)
    search_config_repo_mock.get_by_id.assert_called_once_with(
        non_existent_search_config_id
    )
    search_config_repo_mock.update.assert_not_called()
    assert user_repo_mock.get_by_id.call_count == 0
    assert result is None


def test_update_search_config_use_case_user_not_found():
    search_config_repo_mock = MagicMock()
    user_repo_mock = MagicMock()
    search_config_id = 1
    existing_search_config_entity = SearchConfigEntity(
        id=search_config_id,
        search_term="existing_term",
        is_active=True,
        frequency_days=1,
        preferred_time=time(9, 0),
        user_id=100,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    non_existent_user_id = 999
    update_data = SearchConfigEntity(
        search_term="new_term",
        is_active=False,
        frequency_days=5,
        preferred_time=time(15, 0),
        user_id=non_existent_user_id,
    )
    search_config_repo_mock.get_by_id.return_value = existing_search_config_entity
    user_repo_mock.get_by_id.return_value = None
    use_case = UpdateSearchConfigUseCase(search_config_repo_mock, user_repo_mock)

    with pytest.raises(ValueError) as excinfo:
        use_case.execute(search_config_id, update_data)

    assert f"User with id {non_existent_user_id} not found" in str(excinfo.value)
    search_config_repo_mock.get_by_id.assert_called_once_with(search_config_id)
    user_repo_mock.get_by_id.assert_called_once_with(non_existent_user_id)
    search_config_repo_mock.update.assert_not_called()


def test_get_search_configs_by_user_use_case_success():
    search_config_repo_mock = MagicMock()
    user_repo_mock = MagicMock()
    user_id = 1
    mock_user_entity = UserEntity(
        id=user_id,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_search_configs = [
        SearchConfigEntity(
            id=1,
            search_term="laptops",
            is_active=True,
            frequency_days=7,
            preferred_time=time(10, 30),
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        SearchConfigEntity(
            id=2,
            search_term="smartphones",
            is_active=True,
            frequency_days=3,
            preferred_time=time(14, 0),
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]
    user_repo_mock.get_by_id.return_value = mock_user_entity
    search_config_repo_mock.get_by_user_id.return_value = mock_search_configs
    use_case = GetSearchConfigsByUserUseCase(search_config_repo_mock, user_repo_mock)
    result = use_case.execute(user_id)
    user_repo_mock.get_by_id.assert_called_once_with(user_id)
    search_config_repo_mock.get_by_user_id.assert_called_once_with(user_id)
    assert result == mock_search_configs


def test_get_search_configs_by_user_use_case_user_not_found():
    search_config_repo_mock = MagicMock()
    user_repo_mock = MagicMock()

    non_existent_user_id = 999

    user_repo_mock.get_by_id.return_value = None

    use_case = GetSearchConfigsByUserUseCase(search_config_repo_mock, user_repo_mock)

    with pytest.raises(ValueError) as excinfo:
        use_case.execute(non_existent_user_id)

    assert f"User with id {non_existent_user_id} not found" in str(excinfo.value)
    user_repo_mock.get_by_id.assert_called_once_with(non_existent_user_id)
    search_config_repo_mock.get_by_user_id.assert_not_called()


def test_get_search_configs_by_user_use_case_no_configs_found():
    search_config_repo_mock = MagicMock()
    user_repo_mock = MagicMock()

    user_id = 1
    mock_user_entity = UserEntity(
        id=user_id,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    search_config_repo_mock.get_by_user_id.return_value = []
    user_repo_mock.get_by_id.return_value = mock_user_entity

    use_case = GetSearchConfigsByUserUseCase(search_config_repo_mock, user_repo_mock)

    result = use_case.execute(user_id)

    user_repo_mock.get_by_id.assert_called_once_with(user_id)
    search_config_repo_mock.get_by_user_id.assert_called_once_with(user_id)
    assert result == []


def test_get_search_configs_by_source_website_use_case_no_id():
    search_config_repo_mock = MagicMock()

    source_website_without_id = SourceWebsiteEntity(
        name="Site Without ID",
        base_url="http://no-id.com",
        is_active=True,
    )

    use_case = GetSearchConfigsBySourceWebsiteUseCase(search_config_repo_mock)

    with pytest.raises(ValueError) as excinfo:
        use_case.execute(source_website_without_id)

    assert "SourceWebsite must have an ID to search by." in str(excinfo.value)
    search_config_repo_mock.get_by_source_website_id.assert_not_called()


def test_delete_search_config_use_case_success():
    search_config_repo_mock = MagicMock()
    search_config_id = 1
    search_config_repo_mock.delete.return_value = True
    use_case = DeleteSearchConfigUseCase(search_config_repo_mock)
    result = use_case.execute(search_config_id)
    search_config_repo_mock.delete.assert_called_once_with(search_config_id)
    assert result is True


def test_delete_search_config_use_case_not_found():
    search_config_repo_mock = MagicMock()
    search_config_id = 999
    search_config_repo_mock.delete.return_value = False
    use_case = DeleteSearchConfigUseCase(search_config_repo_mock)
    result = use_case.execute(search_config_id)
    search_config_repo_mock.delete.assert_called_once_with(search_config_id)
    assert result is False


def test_delete_source_website_use_case_success():
    source_website_repo_mock = MagicMock()
    source_website_id = 1
    source_website_repo_mock.delete.return_value = True
    use_case = DeleteSourceWebsiteUseCase(source_website_repo_mock)
    result = use_case.execute(source_website_id)
    source_website_repo_mock.delete.assert_called_once_with(source_website_id)
    assert result is True


def test_delete_source_website_use_case_not_found():
    source_website_repo_mock = MagicMock()
    source_website_id = 999
    source_website_repo_mock.delete.return_value = False
    use_case = DeleteSourceWebsiteUseCase(source_website_repo_mock)
    result = use_case.execute(source_website_id)
    source_website_repo_mock.delete.assert_called_once_with(source_website_id)
    assert result is False
