from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Request, Query
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
    PaginatedSourceWebsiteResponse, SourceWebsiteBulkDeleteRequest,
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
def get_source_website(
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



@router.get("/", response_model=PaginatedSourceWebsiteResponse)
def list_source_websites(
    request: Request,
    limit: int = Query(10, ge=1, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Offset to start fetching items"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: Optional[str] = Query(None, description="Sort order (asc or desc)"),
    source_website_repo: SourceWebsiteRepository = Depends(
        get_source_website_repository
    ),
    current_user: UserEntity = Depends(get_current_active_user),
):
    column_filters = {}

    for param_name, param_value in request.query_params.items():
        if param_name.startswith("filter_") and param_name.endswith("_value"):
            field = param_name.replace("filter_", "").replace("_value", "")
            operator_param_name = f"filter_{field}_operator"
            operator = request.query_params.get(operator_param_name, "equals")

            if field == 'is_active':
                if isinstance(param_value, str):
                    param_value = param_value.lower() == 'true'

            column_filters[field] = {
                "value": param_value,
                "operator": operator
            }

    filter_data = { "column_filters": column_filters }
    use_case = ListSourceWebsitesUseCase(source_website_repo)

    items, total_count = use_case.execute(
        filter_data=filter_data,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )
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
    source_website_entity = SourceWebsiteEntity(id=source_website_id, **source_website.model_dump())
    use_case = UpdateSourceWebsiteUseCase(source_website_repo)
    updated_source_website = use_case.execute(source_website_id, source_website_entity)
    if not updated_source_website:
        raise HTTPException(status_code=404, detail="Source website not found")
    return updated_source_website


@router.delete("/delete/{source_website_id}", status_code=204)
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


@router.delete("/bulk/delete", response_model=dict)
def bulk_delete_source_websites(
    data: SourceWebsiteBulkDeleteRequest,
    source_website_repo: SourceWebsiteRepository = Depends(get_source_website_repository),
    current_user: UserEntity = Depends(get_current_active_user),
):
    deleted = []
    not_found = []
    for sw_id in data.ids:
        use_case = DeleteSourceWebsiteUseCase(source_website_repo)
        if use_case.execute(sw_id):
            deleted.append(sw_id)
        else:
            not_found.append(sw_id)
    return {"deleted": deleted, "not_found": not_found}
