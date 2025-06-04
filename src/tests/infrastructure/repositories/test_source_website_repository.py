from unittest.mock import MagicMock
from types import SimpleNamespace
from datetime import datetime, timezone

from src.app.infrastructure.repositories.source_website_repository import (
    SourceWebsiteRepository,
)
from src.app.entities.source_website import SourceWebsite as SourceWebsiteEntity
from src.app.infrastructure.database.models.source_website_model import (
    SourceWebsite as SourceWebsiteModel,
)


def test_create_source_website():
    db_mock = MagicMock()

    repository = SourceWebsiteRepository(db_mock)

    source_website_entity = SourceWebsiteEntity(
        name="Test Website", base_url="http://test.com", is_active=True
    )

    mock_db_model = SimpleNamespace(
        id=1,
        name="Test Website",
        base_url="http://test.com",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db_mock.add.return_value = None
    db_mock.refresh.side_effect = lambda obj: setattr(obj, "id", mock_db_model.id)
    db_mock.refresh.side_effect = lambda obj: obj.__dict__.update(
        mock_db_model.__dict__
    )

    created_source_website = repository.create(source_website_entity)

    db_mock.add.assert_called_once()

    assert isinstance(db_mock.add.call_args[0][0], SourceWebsiteModel)
    assert db_mock.add.call_args[0][0].name == source_website_entity.name
    assert db_mock.add.call_args[0][0].base_url == source_website_entity.base_url
    assert db_mock.add.call_args[0][0].is_active == source_website_entity.is_active

    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()
    assert created_source_website.id == mock_db_model.id
    assert created_source_website.name == source_website_entity.name
    assert created_source_website.base_url == source_website_entity.base_url
    assert created_source_website.is_active == source_website_entity.is_active
    assert isinstance(created_source_website, SourceWebsiteEntity)


def test_get_source_website_by_id():
    db_mock = MagicMock()

    repository = SourceWebsiteRepository(db_mock)

    mock_db_model = SimpleNamespace(
        id=1,
        name="Existing Website",
        base_url="http://existing.com",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db_mock.query.return_value.filter.return_value.first.return_value = mock_db_model

    found_source_website = repository.get_by_id(1)

    db_mock.query.assert_called_once_with(SourceWebsiteModel)
    db_mock.query.return_value.filter.assert_called_once()
    db_mock.query.return_value.filter.return_value.first.assert_called_once()

    assert found_source_website is not None
    assert found_source_website.id == mock_db_model.id
    assert found_source_website.name == mock_db_model.name
    assert found_source_website.base_url == mock_db_model.base_url
    assert found_source_website.is_active == mock_db_model.is_active
    assert isinstance(found_source_website, SourceWebsiteEntity)


def test_get_source_website_by_id_not_found():
    db_mock = MagicMock()

    repository = SourceWebsiteRepository(db_mock)

    db_mock.query.return_value.filter.return_value.first.return_value = None

    found_source_website = repository.get_by_id(999)

    db_mock.query.assert_called_once_with(SourceWebsiteModel)
    db_mock.query.return_value.filter.assert_called_once()
    db_mock.query.return_value.filter.return_value.first.assert_called_once()

    assert found_source_website is None


def test_get_source_website_by_name():
    db_mock = MagicMock()
    repository = SourceWebsiteRepository(db_mock)

    website_name = "Unique Website Name"

    mock_db_model = SimpleNamespace(
        id=1,
        name=website_name,
        base_url="http://unique-website.com",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db_mock.query.return_value.filter.return_value.first.return_value = mock_db_model

    found_source_website = repository.get_by_name(website_name)

    db_mock.query.assert_called_once_with(SourceWebsiteModel)
    db_mock.query.return_value.filter.assert_called_once()

    filter_arg = db_mock.query.return_value.filter.call_args[0][0]
    assert filter_arg.left.key == "name"
    assert filter_arg.right.value == website_name

    db_mock.query.return_value.filter.return_value.first.assert_called_once()

    assert found_source_website is not None
    assert found_source_website.name == website_name
    assert isinstance(found_source_website, SourceWebsiteEntity)


def test_get_source_website_by_name_not_found():
    db_mock = MagicMock()
    repository = SourceWebsiteRepository(db_mock)

    non_existent_name = "Non Existent Website"

    db_mock.query.return_value.filter.return_value.first.return_value = None

    found_source_website = repository.get_by_name(non_existent_name)

    db_mock.query.assert_called_once_with(SourceWebsiteModel)
    db_mock.query.return_value.filter.assert_called_once()

    filter_arg = db_mock.query.return_value.filter.call_args[0][0]
    assert filter_arg.left.key == "name"
    assert filter_arg.right.value == non_existent_name

    db_mock.query.return_value.filter.return_value.first.assert_called_once()

    assert found_source_website is None


def test_get_all_source_websites():
    db_mock = MagicMock()
    repository = SourceWebsiteRepository(db_mock)

    mock_db_models = [
        SimpleNamespace(
            id=1,
            name="Website A",
            base_url="http://website-a.com",
            is_active=True,
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        ),
        SimpleNamespace(
            id=2,
            name="Website B",
            base_url="http://website-b.com",
            is_active=False,
            created_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
        ),
        SimpleNamespace(
            id=3,
            name="Website C",
            base_url="http://website-c.com",
            is_active=True,
            created_at=datetime(2023, 1, 3, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 3, tzinfo=timezone.utc),
        ),
    ]

    mock_query_obj = MagicMock()
    mock_query_obj.filter.return_value = mock_query_obj
    mock_query_obj.order_by.return_value = mock_query_obj
    mock_query_obj.offset.return_value = mock_query_obj
    mock_query_obj.limit.return_value = mock_query_obj
    mock_query_obj.all.return_value = mock_db_models[0:2]
    mock_query_obj.count.return_value = len(mock_db_models)

    db_mock.query.return_value = mock_query_obj

    column_filters = {"is_active": {"value": True, "operator": "equals"}}
    limit = 2
    offset = 0
    sort_by = "name"
    sort_order = "asc"

    source_websites, total_count = repository.get_all(
        column_filters=column_filters,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    db_mock.query.assert_called_once_with(SourceWebsiteModel)

    mock_query_obj.filter.assert_called_once()

    mock_query_obj.order_by.assert_called_once()

    order_by_arg = mock_query_obj.order_by.call_args[0][0]

    assert order_by_arg.element.key == sort_by

    if sort_order == "asc":
        assert not hasattr(order_by_arg, "_negated") or not order_by_arg._negated
    elif sort_order == "desc":
        assert hasattr(order_by_arg, "_negated") and order_by_arg._negated

    mock_query_obj.offset.assert_called_once_with(offset)
    mock_query_obj.limit.assert_called_once_with(limit)
    mock_query_obj.all.assert_called_once()
    mock_query_obj.count.assert_called_once()

    assert total_count == len(mock_db_models)
    assert len(source_websites) == 2
    assert source_websites[0].name == "Website A"
    assert source_websites[1].name == "Website B"

    for sw in source_websites:
        assert isinstance(sw, SourceWebsiteEntity)


def test_get_all_source_websites_no_filters_default_sort():
    db_mock = MagicMock()
    repository = SourceWebsiteRepository(db_mock)

    mock_db_models = [
        SimpleNamespace(
            id=1,
            name="Website X",
            base_url="http://website-x.com",
            is_active=True,
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        ),
        SimpleNamespace(
            id=2,
            name="Website Y",
            base_url="http://website-y.com",
            is_active=True,
            created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
            updated_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
        ),
    ]

    mock_query_obj = MagicMock()

    mock_query_obj.filter.return_value = mock_query_obj
    mock_query_obj.order_by.return_value = mock_query_obj
    mock_query_obj.offset.return_value = mock_query_obj
    mock_query_obj.limit.return_value = mock_query_obj
    mock_query_obj.all.return_value = mock_db_models
    mock_query_obj.count.return_value = len(mock_db_models)

    db_mock.query.return_value = mock_query_obj

    source_websites, total_count = repository.get_all(limit=10, offset=0)

    db_mock.query.assert_called_once_with(SourceWebsiteModel)
    mock_query_obj.filter.assert_not_called()

    mock_query_obj.order_by.assert_not_called()
    mock_query_obj.offset.assert_called_once_with(0)
    mock_query_obj.limit.assert_called_once_with(10)
    mock_query_obj.all.assert_called_once()
    mock_query_obj.count.assert_called_once()

    assert total_count == len(mock_db_models)
    assert len(source_websites) == len(mock_db_models)
    assert source_websites[0].name == "Website X"
    assert source_websites[1].name == "Website Y"

    for sw in source_websites:
        assert isinstance(sw, SourceWebsiteEntity)


def test_update_source_website():
    db_mock = MagicMock()
    repository = SourceWebsiteRepository(db_mock)

    source_website_id = 1

    existing_db_model = SimpleNamespace(
        id=source_website_id,
        name="Old Name",
        base_url="http://old.com",
        is_active=False,
        created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
    )

    update_entity = SourceWebsiteEntity(
        id=source_website_id, name="New Name", base_url="http://new.com", is_active=True
    )

    db_mock.query.return_value.filter.return_value.first.return_value = (
        existing_db_model
    )

    def refresh_side_effect(obj):
        obj.name = update_entity.name
        obj.base_url = update_entity.base_url
        obj.is_active = update_entity.is_active
        obj.updated_at = datetime.now(timezone.utc)
        obj.__dict__.update(obj.__dict__)

    db_mock.refresh.side_effect = refresh_side_effect

    updated_source_website = repository.update(source_website_id, update_entity)

    db_mock.query.assert_called_once_with(SourceWebsiteModel)
    db_mock.query.return_value.filter.assert_called_once()
    db_mock.query.return_value.filter.return_value.first.assert_called_once()

    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(existing_db_model)

    assert updated_source_website is not None
    assert updated_source_website.id == source_website_id
    assert updated_source_website.name == update_entity.name
    assert updated_source_website.base_url == update_entity.base_url
    assert updated_source_website.is_active == update_entity.is_active
    assert isinstance(updated_source_website, SourceWebsiteEntity)
