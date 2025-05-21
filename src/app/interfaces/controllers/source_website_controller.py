from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session

from src.app.infrastructure.database_config import get_db
from src.app.infrastructure.repositories.source_website_repository import (
    SourceWebsiteRepository,
)
from src.app.security.auth import get_current_active_user
from src.app.use_cases.source_website_use_cases import (
    CreateSourceWebsiteUseCase,
    GetSourceWebsiteByIdUseCase,
    ListSourceWebsitesUseCase,
    UpdateSourceWebsiteUseCase,
    DeleteSourceWebsiteUseCase,
)
from src.app.interfaces.schemas.source_website_schema import (
    SourceWebsiteCreate,
    SourceWebsiteRead,
    SourceWebsiteUpdate,
    PaginatedSourceWebsiteResponse,
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
    created_source_website = use_case.execute(source_website_entity)
    return created_source_website


@router.get("/{source_website_id}", response_model=SourceWebsiteRead)
def get_source_website_by_id(
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


@router.get("/", response_model=PaginatedSourceWebsiteResponse)
def list_source_websites(
    limit: int = Query(10, ge=1, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Offset to start fetching items"),
    source_website_repo: SourceWebsiteRepository = Depends(
        get_source_website_repository
    ),
    current_user: UserEntity = Depends(get_current_active_user),
):
    use_case = ListSourceWebsitesUseCase(source_website_repo)
    items, total_count = use_case.execute(limit=limit, offset=offset)
    return {"items": items, "total_count": total_count, "limit": limit, "offset": offset}


@router.put("/{source_website_id}", response_model=SourceWebsiteRead)
def update_source_website(
    source_website_id: int,
    source_website: SourceWebsiteUpdate,
    source_website_repo: SourceWebsiteRepository = Depends(
        get_source_website_repository
    ),
    current_user: UserEntity = Depends(get_current_active_user),
):
    source_website_entity = SourceWebsiteEntity(**source_website.model_dump())
    use_case = UpdateSourceWebsiteUseCase(source_website_repo)
    updated_source_website = use_case.execute(source_website_id, source_website_entity)
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
    return


@router.delete("/bulk/", response_model=dict)
def bulk_delete_source_websites(
    ids: list[int] = Body(..., embed=True, description="IDs list to delete"),
    source_website_repo: SourceWebsiteRepository = Depends(get_source_website_repository),
    current_user: UserEntity = Depends(get_current_active_user),
):
    deleted = []
    not_found = []
    for sw_id in ids:
        use_case = DeleteSourceWebsiteUseCase(source_website_repo)
        if use_case.execute(sw_id):
            deleted.append(sw_id)
        else:
            not_found.append(sw_id)
    return {"deleted": deleted, "not_found": not_found}
