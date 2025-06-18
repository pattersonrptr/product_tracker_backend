from datetime import datetime
from src.app.entities.user import User


def test_user_minimal_fields():
    user = User(username="john", email="john@example.com", hashed_password="hashed")
    assert user.username == "john"
    assert user.email == "john@example.com"
    assert user.hashed_password == "hashed"
    assert user.is_active is True
    assert user.id is None


def test_user_all_fields():
    now = datetime(2024, 1, 1)
    user = User(
        id=1,
        username="alice",
        email="alice@example.com",
        hashed_password="x",
        is_active=False,
        created_at=now,
        updated_at=now,
    )
    assert user.id == 1
    assert user.is_active is False
    assert user.created_at == now
    assert user.updated_at == now
