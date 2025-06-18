import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from jose import JWTError

from src.app.security import auth


@pytest.fixture
def credentials():
    class Creds:
        credentials = "token"

    return Creds()


@pytest.fixture
def db():
    return MagicMock()


@pytest.mark.asyncio
@patch("src.app.security.auth.jwt.decode")
@patch("src.app.security.auth.UserRepository")
async def test_get_current_user_success(
    mock_user_repo_cls, mock_jwt_decode, credentials, db
):
    mock_jwt_decode.return_value = {"sub": "john"}
    mock_user = MagicMock()
    mock_user.is_active = True
    mock_user_repo = MagicMock()
    mock_user_repo.get_by_username.return_value = mock_user
    mock_user_repo_cls.return_value = mock_user_repo

    user = await auth.get_current_user(credentials, db)
    assert user == mock_user
    mock_jwt_decode.assert_called_once()
    mock_user_repo.get_by_username.assert_called_with(username="john")


@pytest.mark.asyncio
@patch("src.app.security.auth.jwt.decode")
async def test_get_current_user_invalid_token(mock_jwt_decode, credentials, db):
    mock_jwt_decode.side_effect = JWTError()
    with pytest.raises(HTTPException) as exc:
        await auth.get_current_user(credentials, db)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
@patch("src.app.security.auth.jwt.decode")
async def test_get_current_user_no_sub(mock_jwt_decode, credentials, db):
    mock_jwt_decode.return_value = {}
    with pytest.raises(HTTPException) as exc:
        await auth.get_current_user(credentials, db)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
@patch("src.app.security.auth.jwt.decode")
@patch("src.app.security.auth.UserRepository")
async def test_get_current_user_user_not_found(
    mock_user_repo_cls, mock_jwt_decode, credentials, db
):
    mock_jwt_decode.return_value = {"sub": "john"}
    mock_user_repo = MagicMock()
    mock_user_repo.get_by_username.return_value = None
    mock_user_repo_cls.return_value = mock_user_repo

    with pytest.raises(HTTPException) as exc:
        await auth.get_current_user(credentials, db)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_current_active_user_active():
    user = MagicMock()
    user.is_active = True
    result = await auth.get_current_active_user(user)
    assert result == user


@pytest.mark.asyncio
async def test_get_current_active_user_inactive():
    user = MagicMock()
    user.is_active = False
    with pytest.raises(HTTPException) as exc:
        await auth.get_current_active_user(user)
    assert exc.value.status_code == 400
