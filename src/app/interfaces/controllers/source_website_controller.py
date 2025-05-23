from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.infrastructure.database_config import get_db
from src.app.infrastructure.repositories.source_website_repository import (
    SourceWebsiteRepository,
)
from src.app.security.auth import get_current_active_user
from src.app.use_cases.source_website_use_cases import (
    CreateSourceWebsiteUseCase,
    GetSourceWebsiteByIdUseCase,
    GetSourceWebsiteByNameUseCase,
    ListSourceWebsitesUseCase,
    UpdateSourceWebsiteUseCase,
    DeleteSourceWebsiteUseCase,
)
from src.app.interfaces.schemas.source_website_schema import (
    SourceWebsiteCreate,
    SourceWebsiteRead,
    SourceWebsiteUpdate,
)
from src.app.entities.source_website import SourceWebsite as SourceWebsiteEntity
from src.app.entities.user import User as UserEntity

router = APIRouter(prefix="/source_websites", tags=["source_websites"])


def get_source_website_repository(db: Session = Depends(get_db)):
    return SourceWebsiteRepository(db)


@router.post("/", response_model=SourceWebsiteRead, status_code=201)
def create_source_website(
    source_website: SourceWebsiteCreate,
    source_website_repo: SourceWebsiteRepository = Depends(
        get_source_website_repository
    ),
    current_user: UserEntity = Depends(get_current_active_user),
):
    source_website_entity = SourceWebsiteEntity(**source_website.model_dump())
    use_case = CreateSourceWebsiteUseCase(source_website_repo)
    return use_case.execute(source_website_entity)


@router.get("/{source_website_id}", response_model=SourceWebsiteRead)
def read_source_website(
    source_website_id: int,
    source_website_repo: SourceWebsiteRepository = Depends(
        get_source_website_repository
    ),
    current_user: UserEntity = Depends(get_current_active_user),
):
    use_case = GetSourceWebsiteByIdUseCase(source_website_repo)
    source_website = use_case.execute(source_website_id)
    if not source_website:
        raise HTTPException(status_code=404, detail="Source website not found")
    return source_website


@router.get("/name/{name}", response_model=SourceWebsiteRead)
def read_source_website_by_name(
    name: str,
    source_website_repo: SourceWebsiteRepository = Depends(
        get_source_website_repository
    ),
    current_user: UserEntity = Depends(get_current_active_user),
):
    use_case = GetSourceWebsiteByNameUseCase(source_website_repo)
    source_website = use_case.execute(name)
    if not source_website:
        raise HTTPException(status_code=404, detail="Source website not found")
    return source_website


@router.get("/", response_model=List[SourceWebsiteRead])
def list_source_websites(
    source_website_repo: SourceWebsiteRepository = Depends(
        get_source_website_repository
    ),
    current_user: UserEntity = Depends(get_current_active_user),
):
    use_case = ListSourceWebsitesUseCase(source_website_repo)
    return use_case.execute()


@router.put("/{source_website_id}", response_model=SourceWebsiteRead)
def update_source_website(
    source_website_id: int,
    source_website: SourceWebsiteUpdate,
    source_website_repo: SourceWebsiteRepository = Depends(
        get_source_website_repository
    ),
    current_user: UserEntity = Depends(get_current_active_user),
):
    use_case = UpdateSourceWebsiteUseCase(source_website_repo)
    updated_source_website = use_case.execute(source_website_id, source_website)
    if not updated_source_website:
        raise HTTPException(status_code=404, detail="Source website not found")
    return updated_source_website


@router.delete("/{source_website_id}", status_code=204)
def delete_source_website(
    source_website_id: int,
    source_website_repo: SourceWebsiteRepository = Depends(
        get_source_website_repository
    ),
    current_user: UserEntity = Depends(get_current_active_user),
):
    use_case = DeleteSourceWebsiteUseCase(source_website_repo)
    if not use_case.execute(source_website_id):
        raise HTTPException(status_code=404, detail="Source website not found")
    return {"detail": "Source website deleted successfully"}
