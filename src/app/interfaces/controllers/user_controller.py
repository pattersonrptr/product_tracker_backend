import logging

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, UTC
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm

from src.app.interfaces.schemas.auth_schema import TokenPayload
from src.app.interfaces.schemas.user_schema import (
    User as UserResponseSchema,
    UserCreate,
    UserUpdate,
)
from src.app.infrastructure.database_config import get_db
from src.app.infrastructure.repositories.user_repository import UserRepository
from src.app.entities.user import User as UserEntity
from src.app.security.auth import get_current_active_user
from src.config import settings

from src.app.use_cases.user_use_cases import (
    CreateUserUseCase,
    GetUserByIdUseCase,
    GetUserByUsernameUseCase,
    GetAllUsersUseCase,
    UpdateUserUseCase,
    DeleteUserUseCase,
    pwd_context,
    GetUserByEmailUseCase,
)

router = APIRouter(tags=["users"], prefix="/users")
auth_router = APIRouter(tags=["auth"], prefix="/auth")
register_router = APIRouter(tags=["register"])

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


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


@router.post("/", response_model=UserResponseSchema, status_code=201)
def create_user(
    user_in: UserCreate,
    user_repo: UserRepository = Depends(get_user_repository),
    current_user: UserEntity = Depends(get_current_active_user),
):
    hashed_password = hash_password(user_in.password)
    use_case = CreateUserUseCase(user_repo)
    try:
        created_user = use_case.execute(user_in, hashed_password)
        return created_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@register_router.post(
    "/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate, user_repo: UserRepository = Depends(get_user_repository)
):
    hashed_password = hash_password(user_data.password)
    use_case = CreateUserUseCase(user_repo)
    try:
        created_user = use_case.execute(user_data, hashed_password)
        return created_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@auth_router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: UserRepository = Depends(get_user_repository),
):
    get_user_by_username_uc = GetUserByUsernameUseCase(user_repo)
    user = get_user_by_username_uc.execute(form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "email": user.email},
        expires_delta=access_token_expires,
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
        data={
            "sub": current_user.username,
            "user_id": current_user.id,
            "email": current_user.email,
        },
        expires_delta=access_token_expires,
    )
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.get("/", response_model=List[UserResponseSchema])
def read_users(
    user_repo: UserRepository = Depends(get_user_repository),
    current_user: UserEntity = Depends(get_current_active_user),
):
    get_all_users_uc = GetAllUsersUseCase(user_repo)
    users_entities = get_all_users_uc.execute()
    return users_entities


@router.get("/{user_id}", response_model=UserResponseSchema)
def read_user(
    user_id: int,
    user_repo: UserRepository = Depends(get_user_repository),
    current_user: UserEntity = Depends(get_current_active_user),
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's data",
        )

    get_user_by_id_uc = GetUserByIdUseCase(user_repo)
    user_entity = get_user_by_id_uc.execute(user_id)
    if not user_entity:
        raise HTTPException(status_code=404, detail="User not found")
    return user_entity


@router.put("/{user_id}", response_model=UserResponseSchema)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    user_repo: UserRepository = Depends(get_user_repository),
    current_user: UserEntity = Depends(get_current_active_user),
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    update_user_uc = UpdateUserUseCase(user_repo)
    try:
        updated_user_entity = update_user_uc.execute(user_id, user_in)
        if not updated_user_entity:
            raise HTTPException(
                status_code=404, detail="User not found or update failed."
            )
        return updated_user_entity
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during update.",
        )


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    user_repo: UserRepository = Depends(get_user_repository),
    current_user: UserEntity = Depends(get_current_active_user),
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )

    delete_user_uc = DeleteUserUseCase(user_repo)
    deleted = delete_user_uc.execute(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return


@router.get("/username/{username}", response_model=UserResponseSchema)
def read_user_by_username(
    username: str,
    user_repo: UserRepository = Depends(get_user_repository),
    current_user: UserEntity = Depends(get_current_active_user),
):
    if username != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this username's data",
        )

    get_user_by_username_uc = GetUserByUsernameUseCase(user_repo)
    user_entity = get_user_by_username_uc.execute(username)
    if not user_entity:
        raise HTTPException(status_code=404, detail="User not found")
    return user_entity


@router.get("/email/{email}", response_model=UserResponseSchema)
def read_user_by_email(
    email: str,
    user_repo: UserRepository = Depends(get_user_repository),
    current_user: UserEntity = Depends(get_current_active_user),
):
    if email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this email's data",
        )

    get_user_by_email_uc = GetUserByEmailUseCase(user_repo)
    user_entity = get_user_by_email_uc.execute(email)
    if not user_entity:
        raise HTTPException(status_code=404, detail="User not found")
    return user_entity
