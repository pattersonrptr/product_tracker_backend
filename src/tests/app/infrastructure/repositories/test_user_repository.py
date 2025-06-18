from datetime import datetime, timezone

from src.app.infrastructure.repositories.user_repository import UserRepository
from src.app.entities import user as UserEntity


def test_create_user(mocker):
    mock_db = mocker.MagicMock()
    repo = UserRepository(mock_db)
    user_entity = UserEntity.User(
        id=1,
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashedpassword",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_db.refresh.side_effect = lambda obj: [
        setattr(obj, k, getattr(user_entity, k))
        for k in user_entity.model_dump().keys()
    ]

    created_user = repo.create(user_entity)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    assert isinstance(created_user, UserEntity.User)
    assert created_user.username == user_entity.username
    assert created_user.email == user_entity.email
    assert created_user.is_active == user_entity.is_active


def test_get_by_id_found(mocker):
    mock_db = mocker.MagicMock()
    repo = UserRepository(mock_db)
    user_entity = UserEntity.User(
        id=1,
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashedpassword",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_user_model = mocker.Mock(**user_entity.model_dump())
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model

    found_user = repo.get_by_id(1)

    mock_db.query.assert_called_once()
    mock_db.query().filter.assert_called_once()
    mock_db.query().filter().first.assert_called_once()
    assert found_user is not None
    assert isinstance(found_user, UserEntity.User)
    assert found_user.id == user_entity.id
    assert found_user.username == user_entity.username
    assert found_user.email == user_entity.email


def test_get_by_id_not_found(mocker):
    mock_db = mocker.MagicMock()
    repo = UserRepository(mock_db)
    mock_db.query.return_value.filter.return_value.first.return_value = None

    user = repo.get_by_id(999)

    mock_db.query.assert_called_once()
    mock_db.query().filter.assert_called_once()
    mock_db.query().filter().first.assert_called_once()
    assert user is None


def test_get_by_username_found(mocker):
    mock_db = mocker.MagicMock()
    repo = UserRepository(mock_db)
    user_entity = UserEntity.User(
        id=2,
        username="anotheruser",
        email="anotheruser@example.com",
        hashed_password="hashedpassword2",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_user_model = mocker.Mock(**user_entity.model_dump())
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model

    found_user = repo.get_by_username("anotheruser")

    mock_db.query.assert_called_once()
    mock_db.query().filter.assert_called_once()
    mock_db.query().filter().first.assert_called_once()
    assert found_user is not None
    assert isinstance(found_user, UserEntity.User)
    assert found_user.username == user_entity.username
    assert found_user.email == user_entity.email


def test_get_by_username_not_found(mocker):
    mock_db = mocker.MagicMock()
    repo = UserRepository(mock_db)
    mock_db.query.return_value.filter.return_value.first.return_value = None

    user = repo.get_by_username("nonexistentuser")

    mock_db.query.assert_called_once()
    mock_db.query().filter.assert_called_once()
    mock_db.query().filter().first.assert_called_once()
    assert user is None


def test_get_by_email_found(mocker):
    mock_db = mocker.MagicMock()
    repo = UserRepository(mock_db)
    user_entity = UserEntity.User(
        id=3,
        username="emailuser",
        email="emailuser@example.com",
        hashed_password="hashedpassword3",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_user_model = mocker.Mock(**user_entity.model_dump())
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model

    found_user = repo.get_by_email("emailuser@example.com")

    mock_db.query.assert_called_once()
    mock_db.query().filter.assert_called_once()
    mock_db.query().filter().first.assert_called_once()
    assert found_user is not None
    assert isinstance(found_user, UserEntity.User)
    assert found_user.email == user_entity.email
    assert found_user.username == user_entity.username


def test_get_by_email_not_found(mocker):
    mock_db = mocker.MagicMock()
    repo = UserRepository(mock_db)
    mock_db.query.return_value.filter.return_value.first.return_value = None

    user = repo.get_by_email("notfound@example.com")

    mock_db.query.assert_called_once()
    mock_db.query().filter.assert_called_once()
    mock_db.query().filter().first.assert_called_once()
    assert user is None


def test_get_all_users(mocker):
    mock_db = mocker.MagicMock()
    repo = UserRepository(mock_db)
    user_entity_1 = UserEntity.User(
        id=1,
        username="user1",
        email="user1@example.com",
        hashed_password="hashed1",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user_entity_2 = UserEntity.User(
        id=2,
        username="user2",
        email="user2@example.com",
        hashed_password="hashed2",
        is_active=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_user_model_1 = mocker.Mock(**user_entity_1.model_dump())
    mock_user_model_2 = mocker.Mock(**user_entity_2.model_dump())
    mock_db.query.return_value.all.return_value = [mock_user_model_1, mock_user_model_2]

    users = repo.get_all()

    mock_db.query.assert_called_once()
    mock_db.query().all.assert_called_once()
    assert isinstance(users, list)
    assert len(users) == 2
    assert all(isinstance(u, UserEntity.User) for u in users)
    assert users[0].username == "user1"
    assert users[1].username == "user2"


def test_update_user(mocker):
    mock_db = mocker.MagicMock()
    repo = UserRepository(mock_db)
    original_user = UserEntity.User(
        id=1,
        username="user1",
        email="user1@example.com",
        hashed_password="hashed1",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    updated_user = UserEntity.User(
        id=1,
        username="user1_updated",
        email="user1_updated@example.com",
        hashed_password="hashed1",
        is_active=False,
        created_at=original_user.created_at,
        updated_at=datetime.now(timezone.utc),
    )
    mock_user_model = mocker.Mock(**original_user.model_dump())
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model
    mock_db.refresh.side_effect = lambda obj: obj

    result = repo.update(1, updated_user)

    mock_db.query.assert_called_once()
    mock_db.query().filter.assert_called_once()
    mock_db.query().filter().first.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_user_model)

    assert result is not None
    assert isinstance(result, UserEntity.User)
    assert mock_user_model.username == updated_user.username
    assert mock_user_model.email == updated_user.email
    assert mock_user_model.is_active == updated_user.is_active
    assert result.username == updated_user.username
    assert result.email == updated_user.email
    assert result.is_active == updated_user.is_active


def test_delete_user_found(mocker):
    mock_db = mocker.MagicMock()
    repo = UserRepository(mock_db)
    user_entity = UserEntity.User(
        id=1,
        username="user_to_delete",
        email="delete@example.com",
        hashed_password="hashed",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_user_model = mocker.Mock(**user_entity.model_dump())
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model

    result = repo.delete(1)

    mock_db.query.assert_called_once()
    mock_db.query().filter.assert_called_once()
    mock_db.query().filter().first.assert_called_once()
    mock_db.delete.assert_called_once_with(mock_user_model)
    mock_db.commit.assert_called_once()
    assert result is True


def test_delete_user_not_found(mocker):
    mock_db = mocker.MagicMock()
    repo = UserRepository(mock_db)
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = repo.delete(999)

    mock_db.query.assert_called_once()
    mock_db.query().filter.assert_called_once()
    mock_db.query().filter().first.assert_called_once()
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()
    assert result is False
