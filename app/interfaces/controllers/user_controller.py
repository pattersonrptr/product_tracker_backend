from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.use_cases.user_use_cases import UserUseCases
from app.interfaces.schemas.user_schema import (
    User,
    UserCreate,
    UserUpdate,
)
from app.infrastructure.database_config import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from app.entities.user import User as UserEntity  # Importe a CLASSE User

import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter(tags=["users"], prefix="/users")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_use_cases(db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    return UserUseCases(user_repo)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/", response_model=User, status_code=201)
def create_user(
    user_in: UserCreate, use_cases: UserUseCases = Depends(get_user_use_cases)
):
    hashed_password = hash_password(user_in.password)
    user_data = user_in.model_dump(exclude={"password"})
    user = UserEntity(**user_data, hashed_password=hashed_password)
    logging.info(f"Tipo da variável 'user' no controller: {type(user)}")
    return use_cases.create_user(user)


@router.get("/", response_model=List[User])
def read_users(use_cases: UserUseCases = Depends(get_user_use_cases)):
    return use_cases.get_all_users()


@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, use_cases: UserUseCases = Depends(get_user_use_cases)):
    user = use_cases.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    use_cases: UserUseCases = Depends(get_user_use_cases),
):
    user_data = user_in.model_dump(exclude_unset=True)
    existing_user = use_cases.get_user(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_data = {**existing_user.__dict__, **user_data}
    updated_user = UserEntity(**updated_data)
    return use_cases.update_user(user_id, updated_user)


@router.delete("/{user_id}", response_model=bool)
def delete_user(user_id: int, use_cases: UserUseCases = Depends(get_user_use_cases)):
    if not use_cases.get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return use_cases.delete_user(user_id)


@router.get("/username/{username}", response_model=User)
def read_user_by_username(
    username: str, use_cases: UserUseCases = Depends(get_user_use_cases)
):
    user = use_cases.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/email/{email}", response_model=User)
def read_user_by_email(
    email: str, use_cases: UserUseCases = Depends(get_user_use_cases)
):
    user = use_cases.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
