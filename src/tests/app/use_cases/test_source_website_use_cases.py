from unittest.mock import MagicMock
from datetime import datetime, timezone

from src.app.use_cases.source_website_use_cases import (
    CreateSourceWebsiteUseCase,
    GetSourceWebsiteByIdUseCase,
    GetSourceWebsiteByNameUseCase,
    ListSourceWebsitesUseCase,
    UpdateSourceWebsiteUseCase,
    DeleteSourceWebsiteUseCase,
)
from src.app.entities.source_website import SourceWebsite as SourceWebsiteEntity


def test_create_source_website_use_case_success():
    source_website_repo_mock = MagicMock()
    source_website_data = SourceWebsiteEntity(
        name="New Test Website", base_url="http://newtest.com", is_active=True
    )

    mock_created_source_website_entity = SourceWebsiteEntity(
        id=1,
        name="New Test Website",
        base_url="http://newtest.com",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    source_website_repo_mock.get_by_name.return_value = None
    source_website_repo_mock.create.return_value = mock_created_source_website_entity

    use_case = CreateSourceWebsiteUseCase(source_website_repo_mock)

    created_source_website = use_case.execute(source_website=source_website_data)

    source_website_repo_mock.get_by_name.assert_called_once_with(
        source_website_data.name
    )
    source_website_repo_mock.create.assert_called_once_with(source_website_data)
    assert created_source_website == mock_created_source_website_entity


def test_create_source_website_use_case_name_already_registered():
    source_website_repo_mock = MagicMock()

    source_website_data = SourceWebsiteEntity(
        name="Existing Test Website", base_url="http://newtest.com", is_active=True
    )

    mock_existing_source_website_entity = SourceWebsiteEntity(
        id=1,
        name="Existing Test Website",
        base_url="http://existingtest.com",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    source_website_repo_mock.get_by_name.return_value = (
        mock_existing_source_website_entity
    )
    source_website_repo_mock.create.assert_not_called()

    use_case = CreateSourceWebsiteUseCase(source_website_repo_mock)

    result_source_website = use_case.execute(source_website=source_website_data)

    source_website_repo_mock.get_by_name.assert_called_once_with(
        source_website_data.name
    )
    source_website_repo_mock.create.assert_not_called()
    assert result_source_website == mock_existing_source_website_entity


def test_get_source_website_by_id_use_case_success():
    source_website_repo_mock = MagicMock()

    source_website_id = 1

    mock_source_website_entity = SourceWebsiteEntity(
        id=source_website_id,
        name="Test Website",
        base_url="http://test.com",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    source_website_repo_mock.get_by_id.return_value = mock_source_website_entity

    use_case = GetSourceWebsiteByIdUseCase(source_website_repo_mock)

    found_source_website = use_case.execute(source_website_id=source_website_id)

    source_website_repo_mock.get_by_id.assert_called_once_with(source_website_id)
    assert found_source_website == mock_source_website_entity


def test_get_source_website_by_id_use_case_not_found():
    source_website_repo_mock = MagicMock()

    source_website_id = 999

    source_website_repo_mock.get_by_id.return_value = None

    use_case = GetSourceWebsiteByIdUseCase(source_website_repo_mock)

    found_source_website = use_case.execute(source_website_id=source_website_id)

    source_website_repo_mock.get_by_id.assert_called_once_with(source_website_id)
    assert found_source_website is None


def test_get_source_website_by_name_use_case_success():
    source_website_repo_mock = MagicMock()

    source_website_name = "Test Website by Name"

    mock_source_website_entity = SourceWebsiteEntity(
        id=2,
        name=source_website_name,
        base_url="http://testbyname.com",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    source_website_repo_mock.get_by_name.return_value = mock_source_website_entity

    use_case = GetSourceWebsiteByNameUseCase(source_website_repo_mock)

    found_source_website = use_case.execute(name=source_website_name)

    source_website_repo_mock.get_by_name.assert_called_once_with(source_website_name)
    assert found_source_website == mock_source_website_entity


def test_get_source_website_by_name_use_case_not_found():
    source_website_repo_mock = MagicMock()
    source_website_name = "Non-existent Website"
    source_website_repo_mock.get_by_name.return_value = None
    use_case = GetSourceWebsiteByNameUseCase(source_website_repo_mock)
    found_source_website = use_case.execute(name=source_website_name)

    source_website_repo_mock.get_by_name.assert_called_once_with(source_website_name)
    assert found_source_website is None


def test_list_source_websites_use_case_list_all_success():
    source_website_repo_mock = MagicMock()
    mock_source_websites = [
        SourceWebsiteEntity(
            id=1,
            name="Website A",
            base_url="http://websitea.com",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        SourceWebsiteEntity(
            id=2,
            name="Website B",
            base_url="http://websiteb.com",
            is_active=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]
    total_count = len(mock_source_websites)
    source_website_repo_mock.get_all.return_value = (mock_source_websites, total_count)
    use_case = ListSourceWebsitesUseCase(source_website_repo_mock)
    listed_source_websites, actual_total_count = use_case.execute(
        filter_data={}, limit=10, offset=0
    )
    source_website_repo_mock.get_all.assert_called_once_with(
        column_filters={}, limit=10, offset=0, sort_by=None, sort_order=None
    )
    assert listed_source_websites == mock_source_websites
    assert actual_total_count == total_count


def test_list_source_websites_use_case_with_filters_success():
    source_website_repo_mock = MagicMock()
    filter_data = {"column_filters": {"is_active": True}}
    mock_source_websites = [
        SourceWebsiteEntity(
            id=1,
            name="Active Website 1",
            base_url="http://active1.com",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        SourceWebsiteEntity(
            id=3,
            name="Another Active Website",
            base_url="http://anotheractive.com",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]
    total_count = len(mock_source_websites)

    source_website_repo_mock.get_all.return_value = (mock_source_websites, total_count)

    use_case = ListSourceWebsitesUseCase(source_website_repo_mock)

    listed_source_websites, actual_total_count = use_case.execute(
        filter_data=filter_data, limit=10, offset=0
    )

    source_website_repo_mock.get_all.assert_called_once_with(
        column_filters={"is_active": True},
        limit=10,
        offset=0,
        sort_by=None,
        sort_order=None,
    )
    assert listed_source_websites == mock_source_websites
    assert actual_total_count == total_count


def test_list_source_websites_use_case_with_pagination_success():
    source_website_repo_mock = MagicMock()

    test_limit = 1
    test_offset = 1

    mock_source_websites = [
        SourceWebsiteEntity(
            id=2,
            name="Website B",
            base_url="http://websiteb.com",
            is_active=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]
    total_count_in_repo = 2
    source_website_repo_mock.get_all.return_value = (
        mock_source_websites,
        total_count_in_repo,
    )
    use_case = ListSourceWebsitesUseCase(source_website_repo_mock)
    listed_source_websites, actual_total_count = use_case.execute(
        filter_data={}, limit=test_limit, offset=test_offset
    )

    source_website_repo_mock.get_all.assert_called_once_with(
        column_filters={},
        limit=test_limit,
        offset=test_offset,
        sort_by=None,
        sort_order=None,
    )
    assert listed_source_websites == mock_source_websites
    assert actual_total_count == total_count_in_repo


def test_list_source_websites_use_case_with_sorting_success():
    source_website_repo_mock = MagicMock()

    test_sort_by = "name"
    test_sort_order = "desc"

    mock_source_websites = [
        SourceWebsiteEntity(
            id=2,
            name="Website B",
            base_url="http://websiteb.com",
            is_active=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        SourceWebsiteEntity(
            id=1,
            name="Website A",
            base_url="http://websitea.com",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]
    total_count = len(mock_source_websites)

    source_website_repo_mock.get_all.return_value = (mock_source_websites, total_count)

    use_case = ListSourceWebsitesUseCase(source_website_repo_mock)

    listed_source_websites, actual_total_count = use_case.execute(
        filter_data={},
        limit=10,
        offset=0,
        sort_by=test_sort_by,
        sort_order=test_sort_order,
    )

    source_website_repo_mock.get_all.assert_called_once_with(
        column_filters={},
        limit=10,
        offset=0,
        sort_by=test_sort_by,
        sort_order=test_sort_order,
    )
    assert listed_source_websites == mock_source_websites
    assert actual_total_count == total_count


def test_list_source_websites_use_case_no_source_websites_found():
    source_website_repo_mock = MagicMock()
    source_website_repo_mock.get_all.return_value = ([], 0)
    use_case = ListSourceWebsitesUseCase(source_website_repo_mock)
    listed_source_websites, actual_total_count = use_case.execute(
        filter_data={}, limit=10, offset=0
    )

    source_website_repo_mock.get_all.assert_called_once()
    assert listed_source_websites == []
    assert actual_total_count == 0


def test_update_source_website_use_case_success():
    source_website_repo_mock = MagicMock()
    existing_source_website_id = 1

    update_data = SourceWebsiteEntity(
        name="New Name",
        base_url="http://new-url.com",
        is_active=False,
    )

    updated_source_website_entity = SourceWebsiteEntity(
        id=existing_source_website_id,
        name="New Name",
        base_url="http://new-url.com",
        is_active=False,
        # created_at=existing_source_website_entity.created_at,
        # updated_at=datetime.now(timezone.utc),
    )

    source_website_repo_mock.update.return_value = updated_source_website_entity
    use_case = UpdateSourceWebsiteUseCase(source_website_repo_mock)
    result = use_case.execute(existing_source_website_id, update_data)
    source_website_repo_mock.update.assert_called_once_with(
        existing_source_website_id, update_data
    )
    assert result == updated_source_website_entity


def test_update_source_website_use_case_not_found():
    source_website_repo_mock = MagicMock()
    non_existent_source_website_id = 999
    update_data = SourceWebsiteEntity(
        name="Non Existent Name",
        base_url="http://non-existent-url.com",
        is_active=True,
    )
    source_website_repo_mock.update.return_value = None
    use_case = UpdateSourceWebsiteUseCase(source_website_repo_mock)
    result = use_case.execute(non_existent_source_website_id, update_data)
    source_website_repo_mock.update.assert_called_once_with(
        non_existent_source_website_id, update_data
    )
    assert result is None


def test_delete_source_website_use_case_success():
    source_website_repo_mock = MagicMock()
    source_website_id_to_delete = 1
    source_website_repo_mock.delete.return_value = True
    use_case = DeleteSourceWebsiteUseCase(source_website_repo_mock)
    result = use_case.execute(source_website_id_to_delete)
    source_website_repo_mock.delete.assert_called_once_with(source_website_id_to_delete)
    assert result is True


def test_delete_source_website_use_case_not_found():
    source_website_repo_mock = MagicMock()
    non_existent_source_website_id = 999
    source_website_repo_mock.delete.return_value = False
    use_case = DeleteSourceWebsiteUseCase(source_website_repo_mock)
    result = use_case.execute(non_existent_source_website_id)
    source_website_repo_mock.delete.assert_called_once_with(
        non_existent_source_website_id
    )
    assert result is False
