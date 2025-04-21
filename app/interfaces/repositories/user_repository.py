from typing import Optional, List
from abc import ABC, abstractmethod

from app.entities import user as UserEntity


class UserRepositoryInterface(ABC):
    @abstractmethod
    def create(self, user: UserEntity.User) -> UserEntity.User:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserEntity.User]:
        raise NotImplementedError

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[UserEntity.User]:
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserEntity.User]:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[UserEntity.User]:
        raise NotImplementedError

    @abstractmethod
    def update(self, user_id: int, user: UserEntity.User) -> Optional[UserEntity.User]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        raise NotImplementedError
