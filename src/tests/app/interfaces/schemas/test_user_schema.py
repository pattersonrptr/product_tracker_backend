import pytest
from datetime import datetime
from pydantic import ValidationError

from src.app.interfaces.schemas.user_schema import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    User,
)


def test_user_base_valid():
    obj = UserBase(username="john", email="john@example.com")
    assert obj.username == "john"
    assert obj.email == "john@example.com"


def test_user_create_valid():
    obj = UserCreate(username="john", email="john@example.com", password="123456")
    assert obj.password == "123456"


def test_user_create_password_too_short():
    with pytest.raises(ValidationError):
        UserCreate(username="john", email="john@example.com", password="123")


def test_user_update_partial():
    obj = UserUpdate(username="jane")
    assert obj.username == "jane"
    assert obj.email is None


def test_user_update_password_fields():
    obj = UserUpdate(current_password="abcdef", new_password="ghijkl")
    assert obj.current_password == "abcdef"
    assert obj.new_password == "ghijkl"


def test_user_in_db():
    now = datetime.utcnow()
    obj = UserInDB(
        id=1,
        username="john",
        email="john@example.com",
        hashed_password="hashed",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    assert obj.id == 1
    assert obj.is_active


def test_user():
    now = datetime.utcnow()
    obj = User(
        id=2,
        username="jane",
        email="jane@example.com",
        is_active=False,
        created_at=now,
        updated_at=now,
    )
    assert obj.id == 2
    assert not obj.is_active


def test_user_base_invalid_email():
    with pytest.raises(ValidationError):
        UserBase(username="john", email="not-an-email")
