from typing import Optional, List

from sqlalchemy.orm import Session

from app.infrastructure.database.models.user_model import User as UserModel
from app.entities import user as UserEntity
from app.interfaces.repositories.user_repository import UserRepositoryInterface


class UserRepository(UserRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: UserEntity.User) -> UserEntity.User:
        try:
            db_user = UserModel(**user.__dict__)
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return UserEntity.User(**db_user.__dict__)
        except Exception as e:
            self.db.rollback()
            raise e

    def get_by_id(self, user_id: int) -> Optional[UserEntity.User]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return UserEntity.User(**db_user.__dict__) if db_user else None

    def get_by_username(self, username: str) -> Optional[UserEntity.User]:
        db_user = (
            self.db.query(UserModel).filter(UserModel.username == username).first()
        )
        return UserEntity.User(**db_user.__dict__) if db_user else None

    def get_by_email(self, email: str) -> Optional[UserEntity.User]:
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        return UserEntity.User(**db_user.__dict__) if db_user else None

    def get_all(self) -> List[UserEntity.User]:
        db_users = self.db.query(UserModel).all()
        return [UserEntity.User(**db_user.__dict__) for db_user in db_users]

    def update(self, user_id: int, user: UserEntity.User) -> Optional[UserEntity.User]:
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None
        try:
            for key, value in user.__dict__.items():
                if key != "id":
                    setattr(db_user, key, value)
            self.db.commit()
            self.db.refresh(db_user)
            return UserEntity.User(**db_user.__dict__)
        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, user_id: int) -> bool:
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False
        try:
            self.db.delete(db_user)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
