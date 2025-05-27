from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime, UTC
from jose import jwt, JWTError

from src.app.interfaces.schemas.auth_schema import TokenPayload
from src.app.use_cases.user_use_cases import UserUseCases
from src.app.interfaces.schemas.user_schema import (
    User,
    UserCreate,
    UserUpdate,
)
from src.app.infrastructure.database_config import get_db
from src.app.infrastructure.repositories.user_repository import UserRepository
from src.app.entities.user import User as UserEntity
from src.app.security.auth import get_current_active_user
from src.config import settings


router = APIRouter(tags=["users"], prefix="/users")
auth_router = APIRouter(tags=["auth"], prefix="/auth")
register_router = APIRouter(tags=["register"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_use_cases(db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    return UserUseCases(user_repo)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


@router.post("/", response_model=User, status_code=201)
def create_user(
    user_in: UserCreate,
    use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
):
    hashed_password = hash_password(user_in.password)
    user_data = user_in.model_dump(exclude={"password"})
    user = UserEntity(**user_data, hashed_password=hashed_password)
    return use_cases.create_user(user)


@register_router.post(
    "/register", response_model=User, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate, user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    existing_user_by_username = user_use_cases.get_user_by_username(
        username=user_data.username
    )

    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already registered"
        )

    existing_user_by_email = user_use_cases.get_user_by_email(email=user_data.email)

    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    hashed_password = pwd_context.hash(user_data.password)

    new_user_entity = UserEntity(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True,
    )

    created_user = user_use_cases.create_user(user=new_user_entity)

    return created_user


@auth_router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_cases: UserUseCases = Depends(get_user_use_cases),
    db: Session = Depends(get_db),
):
    user = use_cases.get_user_by_username(form_data.username)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/verify-token")
async def verify_token(payload: TokenPayload):
    try:
        jwt.decode(payload.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return {"is_valid": True}
    except JWTError:
        return {"is_valid": False}


@auth_router.post("/refresh-token")
async def refresh_token(current_user: UserEntity = Depends(get_current_active_user)):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.get("/", response_model=List[User])
def read_users(
    use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
):
    return use_cases.get_all_users()


@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: int,
    use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
):
    user = use_cases.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
):
    user_data = user_in.model_dump(exclude_unset=True)
    existing_user = use_cases.get_user(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_data = {**existing_user.__dict__, **user_data}
    updated_user = UserEntity(**updated_data)
    return use_cases.update_user(user_id, updated_user)


@router.delete("/{user_id}", response_model=bool)
def delete_user(
    user_id: int,
    use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
):
    if not use_cases.get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return use_cases.delete_user(user_id)


@router.get("/username/{username}", response_model=User)
def read_user_by_username(
    username: str,
    use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
):
    user = use_cases.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/email/{email}", response_model=User)
def read_user_by_email(
    email: str,
    use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
):
    user = use_cases.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
