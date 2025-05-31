from typing import Optional, List
from src.app.entities import user as UserEntity
from src.app.interfaces.repositories.user_repository import UserRepositoryInterface
from src.app.interfaces.schemas.user_schema import UserCreate, UserUpdate


class CreateUserUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    def execute(self, user_data: UserCreate, hashed_password: str) -> UserEntity.User:
        existing_user_by_username = self.user_repo.get_by_username(user_data.username)
        if existing_user_by_username:
            raise ValueError("Username already registered")

        existing_user_by_email = self.user_repo.get_by_email(user_data.email)
        if existing_user_by_email:
            raise ValueError("Email already registered")

        new_user_entity = UserEntity.User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True,
        )
        created_user = self.user_repo.create(new_user_entity)
        return created_user


class GetUserByIdUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    def execute(self, user_id: int) -> Optional[UserEntity.User]:
        return self.user_repo.get_by_id(user_id)


class GetUserByUsernameUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    def execute(self, username: str) -> Optional[UserEntity.User]:
        return self.user_repo.get_by_username(username)


class GetUserByEmailUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    def execute(self, email: str) -> Optional[UserEntity.User]:
        return self.user_repo.get_by_email(email)


class GetAllUsersUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    def execute(self) -> List[UserEntity.User]:
        return self.user_repo.get_all()


class UpdateUserUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    def execute(self, user_id: int, user_in: UserUpdate) -> Optional[UserEntity.User]:
        existing_user = self.user_repo.get_by_id(user_id)
        if not existing_user:
            return None

        user_data = user_in.model_dump(exclude_unset=True)

        if "username" in user_data and user_data["username"] != existing_user.username:
            if self.user_repo.get_by_username(user_data["username"]):
                raise ValueError("New username already registered")

        if "email" in user_data and user_data["email"] != existing_user.email:
            if self.user_repo.get_by_email(user_data["email"]):
                raise ValueError("New email already registered by another user")

        for key, value in user_data.items():
            setattr(existing_user, key, value)

        return self.user_repo.update(user_id, existing_user)


class DeleteUserUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    def execute(self, user_id: int) -> bool:
        return self.user_repo.delete(user_id)
