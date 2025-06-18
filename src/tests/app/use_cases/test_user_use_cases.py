import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from src.app.use_cases.user_use_cases import (
    CreateUserUseCase,
    GetUserByIdUseCase,
    GetUserByUsernameUseCase,
    GetUserByEmailUseCase,
    GetAllUsersUseCase,
    UpdateUserUseCase,
    pwd_context,
    DeleteUserUseCase,
)
from src.app.entities import user as UserEntity
from src.app.interfaces.schemas.user_schema import UserCreate, UserUpdate


def test_create_user_use_case_success():
    user_repo_mock = MagicMock()
    user_create_data = UserCreate(
        username="newuser", email="newuser@example.com", password="securepassword"
    )
    hashed_password = "hashed_securepassword"
    mock_created_user_entity = UserEntity.User(
        id=1,
        username="newuser",
        email="newuser@example.com",
        hashed_password=hashed_password,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user_repo_mock.get_by_username.return_value = None
    user_repo_mock.get_by_email.return_value = None
    user_repo_mock.create.return_value = mock_created_user_entity
    use_case = CreateUserUseCase(user_repo_mock)
    created_user = use_case.execute(user_create_data, hashed_password)
    user_repo_mock.get_by_username.assert_called_once_with(user_create_data.username)
    user_repo_mock.get_by_email.assert_called_once_with(user_create_data.email)
    user_repo_mock.create.assert_called_once()
    called_user_entity = user_repo_mock.create.call_args[0][0]
    assert isinstance(called_user_entity, UserEntity.User)
    assert called_user_entity.username == user_create_data.username
    assert called_user_entity.email == user_create_data.email
    assert called_user_entity.hashed_password == hashed_password
    assert called_user_entity.is_active is True
    assert created_user == mock_created_user_entity
    assert isinstance(created_user, UserEntity.User)


def test_create_user_use_case_username_already_registered():
    user_repo_mock = MagicMock()
    user_create_data = UserCreate(
        username="existinguser", email="newuser@example.com", password="securepassword"
    )
    hashed_password = "hashed_securepassword"
    mock_existing_user_by_username = UserEntity.User(
        id=1,
        username="existinguser",
        email="existing@example.com",
        hashed_password="some_hashed_password",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user_repo_mock.get_by_username.return_value = mock_existing_user_by_username
    user_repo_mock.get_by_email.return_value = None
    use_case = CreateUserUseCase(user_repo_mock)
    with pytest.raises(ValueError) as excinfo:
        use_case.execute(user_create_data, hashed_password)
    user_repo_mock.get_by_username.assert_called_once_with(user_create_data.username)
    user_repo_mock.get_by_email.assert_not_called()
    user_repo_mock.create.assert_not_called()
    assert str(excinfo.value) == "Username already registered"


def test_create_user_use_case_email_already_registered():
    user_repo_mock = MagicMock()
    user_create_data = UserCreate(
        username="newuniqueuser",
        email="existing@example.com",
        password="securepassword",
    )
    hashed_password = "hashed_securepassword"
    mock_existing_user_by_email = UserEntity.User(
        id=2,
        username="anotheruser",
        email="existing@example.com",
        hashed_password="some_other_hashed_password",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user_repo_mock.get_by_username.return_value = None
    user_repo_mock.get_by_email.return_value = mock_existing_user_by_email
    use_case = CreateUserUseCase(user_repo_mock)
    with pytest.raises(ValueError) as excinfo:
        use_case.execute(user_create_data, hashed_password)
    user_repo_mock.get_by_username.assert_called_once_with(user_create_data.username)
    user_repo_mock.get_by_email.assert_called_once_with(user_create_data.email)
    user_repo_mock.create.assert_not_called()
    assert str(excinfo.value) == "Email already registered"


def test_get_user_by_id_use_case_success():
    user_repo_mock = MagicMock()
    user_id = 1
    mock_user_entity = UserEntity.User(
        id=user_id,
        username="testuser",
        email="test@example.com",
        hashed_password="some_hashed_password",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user_repo_mock.get_by_id.return_value = mock_user_entity
    use_case = GetUserByIdUseCase(user_repo_mock)
    found_user = use_case.execute(user_id)
    user_repo_mock.get_by_id.assert_called_once_with(user_id)
    assert found_user == mock_user_entity
    assert isinstance(found_user, UserEntity.User)


def test_get_user_by_id_use_case_not_found():
    user_repo_mock = MagicMock()
    user_id = 999
    user_repo_mock.get_by_id.return_value = None
    use_case = GetUserByIdUseCase(user_repo_mock)
    found_user = use_case.execute(user_id)
    user_repo_mock.get_by_id.assert_called_once_with(user_id)
    assert found_user is None


def test_get_user_by_username_use_case_success():
    user_repo_mock = MagicMock()
    test_username = "uniqueusername"
    mock_user_entity = UserEntity.User(
        id=1,
        username=test_username,
        email="user@example.com",
        hashed_password="some_hashed_password",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user_repo_mock.get_by_username.return_value = mock_user_entity
    use_case = GetUserByUsernameUseCase(user_repo_mock)
    found_user = use_case.execute(test_username)
    user_repo_mock.get_by_username.assert_called_once_with(test_username)
    assert found_user == mock_user_entity
    assert isinstance(found_user, UserEntity.User)


def test_get_user_by_username_use_case_not_found():
    user_repo_mock = MagicMock()
    test_username = "nonexistentuser"
    user_repo_mock.get_by_username.return_value = None
    use_case = GetUserByUsernameUseCase(user_repo_mock)
    found_user = use_case.execute(test_username)
    user_repo_mock.get_by_username.assert_called_once_with(test_username)
    assert found_user is None


def test_get_user_by_email_use_case_success():
    user_repo_mock = MagicMock()
    test_email = "unique@example.com"
    mock_user_entity = UserEntity.User(
        id=1,
        username="emailtestuser",
        email=test_email,
        hashed_password="some_hashed_password",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user_repo_mock.get_by_email.return_value = mock_user_entity
    use_case = GetUserByEmailUseCase(user_repo_mock)
    found_user = use_case.execute(test_email)
    user_repo_mock.get_by_email.assert_called_once_with(test_email)
    assert found_user == mock_user_entity
    assert isinstance(found_user, UserEntity.User)


def test_get_user_by_email_use_case_not_found():
    user_repo_mock = MagicMock()
    test_email = "nonexistent@example.com"
    user_repo_mock.get_by_email.return_value = None
    use_case = GetUserByEmailUseCase(user_repo_mock)
    found_user = use_case.execute(test_email)
    user_repo_mock.get_by_email.assert_called_once_with(test_email)
    assert found_user is None


def test_list_users_use_case_success():
    user_repo_mock = MagicMock()
    mock_users_list = [
        UserEntity.User(
            id=1,
            username="user1",
            email="user1@example.com",
            hashed_password="hash1",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        UserEntity.User(
            id=2,
            username="user2",
            email="user2@example.com",
            hashed_password="hash2",
            is_active=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]
    user_repo_mock.get_all.return_value = mock_users_list
    use_case = GetAllUsersUseCase(user_repo_mock)
    found_users = use_case.execute()
    user_repo_mock.get_all.assert_called_once()
    assert found_users == mock_users_list
    assert len(found_users) == 2
    assert all(isinstance(user, UserEntity.User) for user in found_users)


def test_get_all_users_use_case_with_pagination():
    user_repo_mock = MagicMock()
    full_mock_users_list = [
        UserEntity.User(
            id=i,
            username=f"user{i}",
            email=f"user{i}@example.com",
            hashed_password=f"hash{i}",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        for i in range(1, 11)
    ]
    skip_value = 2
    limit_value = 5
    expected_paged_users = full_mock_users_list[skip_value : skip_value + limit_value]
    user_repo_mock.get_all.return_value = expected_paged_users
    use_case = GetAllUsersUseCase(user_repo_mock)
    found_users = use_case.execute(skip=skip_value, limit=limit_value)
    user_repo_mock.get_all.assert_called_once_with(skip=skip_value, limit=limit_value)
    assert found_users == expected_paged_users
    assert len(found_users) == limit_value
    assert all(isinstance(user, UserEntity.User) for user in found_users)


def test_update_user_use_case_success_non_password_fields():
    user_repo_mock = MagicMock()
    existing_user = UserEntity.User(
        id=1,
        username="oldusername",
        email="oldemail@example.com",
        hashed_password=pwd_context.hash("oldpassword"),
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    update_data = UserUpdate(
        username="newusername", email="newemail@example.com", is_active=False
    )
    updated_user_entity = UserEntity.User(
        id=1,
        username=update_data.username,
        email=update_data.email,
        hashed_password=existing_user.hashed_password,
        is_active=update_data.is_active,
        created_at=existing_user.created_at,
        updated_at=datetime.now(timezone.utc),
    )
    user_repo_mock.get_by_id.return_value = existing_user
    user_repo_mock.get_by_username.return_value = None
    user_repo_mock.get_by_email.return_value = None
    user_repo_mock.update.return_value = updated_user_entity
    use_case = UpdateUserUseCase(user_repo_mock)
    result_user = use_case.execute(user_id=1, user_in=update_data)
    user_repo_mock.get_by_id.assert_called_once_with(1)
    user_repo_mock.get_by_username.assert_called_once_with(update_data.username)
    user_repo_mock.get_by_email.assert_called_once_with(update_data.email)
    args, kwargs = user_repo_mock.update.call_args
    called_user_id = args[0]
    called_user_entity = args[1]
    assert called_user_id == 1
    assert called_user_entity.username == update_data.username
    assert called_user_entity.email == update_data.email
    assert called_user_entity.is_active == update_data.is_active
    assert called_user_entity.hashed_password == existing_user.hashed_password
    assert result_user == updated_user_entity
    assert isinstance(result_user, UserEntity.User)
    assert result_user.username == "newusername"
    assert result_user.email == "newemail@example.com"
    assert result_user.is_active is False


def test_update_user_use_case_user_not_found():
    user_repo_mock = MagicMock()
    user_repo_mock.get_by_id.return_value = None
    update_data = UserUpdate(
        username="anyusername", email="anyemail@example.com", is_active=True
    )
    use_case = UpdateUserUseCase(user_repo_mock)
    result = use_case.execute(user_id=999, user_in=update_data)
    user_repo_mock.get_by_id.assert_called_once_with(999)
    user_repo_mock.update.assert_not_called()
    user_repo_mock.get_by_username.assert_not_called()
    user_repo_mock.get_by_email.assert_not_called()
    assert result is None


def test_update_user_use_case_success_password_change():
    user_repo_mock = MagicMock()
    old_password = "oldsecurepassword"
    new_password = "newsecurepassword"
    hashed_old_password = pwd_context.hash(old_password)
    hashed_new_password = pwd_context.hash(new_password)
    fixed_created_at = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    fixed_existing_updated_at = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    existing_user = UserEntity.User(
        id=1,
        username="existinguser",
        email="existing@example.com",
        hashed_password=hashed_old_password,
        is_active=True,
        created_at=fixed_created_at,
        updated_at=fixed_existing_updated_at,
    )
    mock_updated_at_after_update = datetime(2023, 1, 1, 10, 0, 5, tzinfo=timezone.utc)
    updated_user_entity = UserEntity.User(
        id=1,
        username="existinguser",
        email="existing@example.com",
        hashed_password=hashed_new_password,
        is_active=True,
        created_at=existing_user.created_at,
        updated_at=mock_updated_at_after_update,
    )
    user_repo_mock.get_by_id.return_value = existing_user
    user_repo_mock.update.return_value = updated_user_entity
    with patch("src.app.use_cases.user_use_cases.pwd_context") as mock_pwd_context:
        mock_pwd_context.verify.return_value = True
        mock_pwd_context.hash.return_value = hashed_new_password
        update_data = UserUpdate(
            current_password=old_password, new_password=new_password
        )
        use_case = UpdateUserUseCase(user_repo_mock)
        result_user = use_case.execute(user_id=1, user_in=update_data)
        user_repo_mock.get_by_id.assert_called_once_with(1)
        mock_pwd_context.verify.assert_called_once_with(
            old_password, hashed_old_password
        )
        mock_pwd_context.hash.assert_called_once_with(new_password)
        user_repo_mock.get_by_username.assert_not_called()
        user_repo_mock.get_by_email.assert_not_called()
        args, kwargs = user_repo_mock.update.call_args
        called_user_id = args[0]
        called_user_entity = args[1]
        assert called_user_id == 1
        assert called_user_entity.username == existing_user.username
        assert called_user_entity.email == existing_user.email
        assert called_user_entity.hashed_password == hashed_new_password
        assert called_user_entity.is_active == existing_user.is_active
        # assert called_user_entity.created_at == existing_user.created_at
        # assert called_user_entity.updated_at > existing_user.updated_at
        assert result_user.id == updated_user_entity.id
        assert result_user.username == updated_user_entity.username
        assert result_user.email == updated_user_entity.email
        assert result_user.hashed_password == updated_user_entity.hashed_password
        assert result_user.is_active == updated_user_entity.is_active
        # assert result_user.created_at == updated_user_entity.created_at
        # assert result_user.updated_at == updated_user_entity.updated_at


def test_update_user_use_case_incorrect_current_password():
    user_repo_mock = MagicMock()
    correct_old_password = "oldsecurepassword"
    incorrect_current_password = "wrongpassword"
    new_password = "newsecurepassword"
    hashed_old_password = pwd_context.hash(correct_old_password)
    existing_user = UserEntity.User(
        id=1,
        username="existinguser",
        email="existing@example.com",
        hashed_password=hashed_old_password,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user_repo_mock.get_by_id.return_value = existing_user
    with patch("src.app.use_cases.user_use_cases.pwd_context") as mock_pwd_context:
        mock_pwd_context.verify.return_value = False
        update_data = UserUpdate(
            current_password=incorrect_current_password, new_password=new_password
        )
        use_case = UpdateUserUseCase(user_repo_mock)
        with pytest.raises(ValueError) as excinfo:
            use_case.execute(user_id=1, user_in=update_data)
        assert str(excinfo.value) == "Incorrect current password."
        user_repo_mock.get_by_id.assert_called_once_with(1)
        mock_pwd_context.verify.assert_called_once_with(
            incorrect_current_password, hashed_old_password
        )
        mock_pwd_context.hash.assert_not_called()
        user_repo_mock.update.assert_not_called()
        user_repo_mock.get_by_username.assert_not_called()
        user_repo_mock.get_by_email.assert_not_called()


def test_update_user_use_case_new_username_already_registered():
    user_repo_mock = MagicMock()
    existing_user = UserEntity.User(
        id=1,
        username="originalusername",
        email="original@example.com",
        hashed_password="hashedpassword",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    conflicting_user = UserEntity.User(
        id=2,
        username="existingusername",
        email="another@example.com",
        hashed_password="anotherhashedpassword",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user_repo_mock.get_by_id.return_value = existing_user
    user_repo_mock.get_by_username.return_value = conflicting_user
    update_data = UserUpdate(username="existingusername")
    use_case = UpdateUserUseCase(user_repo_mock)
    with pytest.raises(ValueError) as excinfo:
        use_case.execute(user_id=1, user_in=update_data)
    assert str(excinfo.value) == "New username already registered"
    user_repo_mock.get_by_id.assert_called_once_with(1)
    user_repo_mock.get_by_username.assert_called_once_with("existingusername")
    user_repo_mock.update.assert_not_called()
    user_repo_mock.get_by_email.assert_not_called()


def test_update_user_use_case_new_email_already_registered():
    user_repo_mock = MagicMock()
    existing_user = UserEntity.User(
        id=1,
        username="originaluser",
        email="original@example.com",
        hashed_password="hashedpassword",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    conflicting_user = UserEntity.User(
        id=2,
        username="anotheruser",
        email="existing@example.com",
        hashed_password="anotherhashedpassword",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user_repo_mock.get_by_id.return_value = existing_user
    user_repo_mock.get_by_email.return_value = conflicting_user
    update_data = UserUpdate(email="existing@example.com")
    use_case = UpdateUserUseCase(user_repo_mock)
    with pytest.raises(ValueError) as excinfo:
        use_case.execute(user_id=1, user_in=update_data)
    assert str(excinfo.value) == "New email already registered by another user"
    user_repo_mock.get_by_id.assert_called_once_with(1)
    user_repo_mock.get_by_email.assert_called_once_with("existing@example.com")
    user_repo_mock.update.assert_not_called()
    user_repo_mock.get_by_username.assert_not_called()


def test_update_user_use_case_no_current_password_for_new_password():
    user_repo_mock = MagicMock()
    existing_user = UserEntity.User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password=pwd_context.hash("currentpassword"),
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user_repo_mock.get_by_id.return_value = existing_user
    update_data = UserUpdate(new_password="newsecurepassword")
    use_case = UpdateUserUseCase(user_repo_mock)
    with pytest.raises(ValueError) as excinfo:
        use_case.execute(user_id=1, user_in=update_data)
    assert str(excinfo.value) == "Current password is required to set a new password."
    user_repo_mock.get_by_id.assert_called_once_with(1)
    user_repo_mock.update.assert_not_called()
    user_repo_mock.get_by_username.assert_not_called()
    user_repo_mock.get_by_email.assert_not_called()


def test_delete_user_use_case_success():
    user_repo_mock = MagicMock()
    user_id_to_delete = 1
    user_repo_mock.delete.return_value = True
    use_case = DeleteUserUseCase(user_repo_mock)
    result = use_case.execute(user_id=user_id_to_delete)
    user_repo_mock.delete.assert_called_once_with(user_id_to_delete)
    assert result is True


def test_delete_user_use_case_user_not_found():
    user_repo_mock = MagicMock()
    user_id_to_delete = 999
    user_repo_mock.delete.return_value = False
    use_case = DeleteUserUseCase(user_repo_mock)
    result = use_case.execute(user_id=user_id_to_delete)
    user_repo_mock.delete.assert_called_once_with(user_id_to_delete)
    assert result is False
