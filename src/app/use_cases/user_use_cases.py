from typing import Optional, List

from sqlalchemy.orm import Session  # noqa: F401

from src.app.entities import user as UserEntity
from src.app.interfaces.repositories.user_repository import UserRepositoryInterface


class UserUseCases:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    def create_user(self, user: UserEntity.User) -> UserEntity.User:
        return self.user_repo.create(user)

    def get_user(self, user_id: int) -> Optional[UserEntity.User]:
        return self.user_repo.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[UserEntity.User]:
        return self.user_repo.get_by_username(username)

    def get_user_by_email(self, email: str) -> Optional[UserEntity.User]:
        return self.user_repo.get_by_email(email)

    def get_all_users(self) -> List[UserEntity.User]:
        return self.user_repo.get_all()

    def update_user(
        self, user_id: int, user: UserEntity.User
    ) -> Optional[UserEntity.User]:
        existing_user = self.user_repo.get_by_id(user_id)
        if not existing_user:
            return None
        user.id = user_id
        return self.user_repo.update(user_id, user)

    def delete_user(self, user_id: int) -> bool:
        return self.user_repo.delete(user_id)
