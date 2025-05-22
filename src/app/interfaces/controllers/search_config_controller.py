from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Body, Request, Query
from sqlalchemy.orm import Session

from src.app.entities.user import User as UserEntity
from src.app.entities import search_config as SearchConfigEntity
from src.app.security.auth import get_current_active_user
from src.app.use_cases.search_config_use_cases import (
    CreateSearchConfigUseCase,
    GetSearchConfigUseCase,
    ListSearchConfigsUseCase,
    UpdateSearchConfigUseCase,
    DeleteSearchConfigUseCase,
    GetSearchConfigsByUserUseCase,
    GetSearchConfigsBySourceWebsiteUseCase,
)
from src.app.interfaces.schemas.search_config_schema import (
    SearchConfig,
    SearchConfigCreate,
    SearchConfigUpdate, PaginatedSearchConfigResponse,
)
from src.app.infrastructure.database_config import get_db
from src.app.infrastructure.repositories.search_config_repository import (
    SearchConfigRepository,
)
from src.app.infrastructure.repositories.user_repository import UserRepository
from src.app.infrastructure.repositories.source_website_repository import (
    SourceWebsiteRepository,
)

router = APIRouter(prefix="/search_configs", tags=["search_config"])


def get_repos(db: Session = Depends(get_db)):
    return {
        "search_config_repo": SearchConfigRepository(db),
        "user_repo": UserRepository(db),
        "source_website_repo": SourceWebsiteRepository(db),
    }


@router.post("/", response_model=SearchConfig, status_code=201)
def create_search_config(
    search_config_in: SearchConfigCreate,
    repos=Depends(get_repos),
    current_user: UserEntity = Depends(get_current_active_user),
):
    source_websites = []
    if search_config_in.source_websites:
        for sw_id in search_config_in.source_websites:
            db_sw = repos["source_website_repo"].get_by_id(sw_id)
            if db_sw:
                source_websites.append(db_sw)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Source website with id {sw_id} not found",
                )

    search_config = SearchConfigEntity.SearchConfig(
        **search_config_in.model_dump(exclude={"source_websites"}),
        source_websites=source_websites,
    )
    use_case = CreateSearchConfigUseCase(repos["search_config_repo"], repos["user_repo"])
    try:
        return use_case.execute(search_config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PaginatedSearchConfigResponse)
def read_search_configs(
    request: Request,
    limit: int = Query(10, ge=1, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Offset to start fetching items"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: Optional[str] = Query(None, description="Sort order (asc or desc)"),
    repos=Depends(get_repos),
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

    filter_data = {"column_filters": column_filters}
    use_case = ListSearchConfigsUseCase(repos["search_config_repo"])

    items, total_count = use_case.execute(
        filter_data=filter_data,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return {"items": items, "total_count": total_count, "limit": limit, "offset": offset}


@router.get("/{search_config_id}", response_model=SearchConfig)
def read_search_config(
    search_config_id: int,
    repos=Depends(get_repos),
    current_user: UserEntity = Depends(get_current_active_user),
):
    use_case = GetSearchConfigUseCase(repos["search_config_repo"])
    search_config = use_case.execute(search_config_id)
    if not search_config:
        raise HTTPException(status_code=404, detail="Search config not found")
    return search_config


@router.put("/{search_config_id}", response_model=SearchConfig)
def update_search_config(
    search_config_id: int,
    search_config_in: SearchConfigUpdate,
    repos=Depends(get_repos),
    current_user: UserEntity = Depends(get_current_active_user),
):
    source_websites_models = []
    if search_config_in.source_websites:
        for sw_id in search_config_in.source_websites:
            db_sw = repos["source_website_repo"].get_by_id(sw_id)
            if db_sw:
                source_websites_models.append(db_sw)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Source website with id {sw_id} not found",
                )

    search_config = SearchConfigEntity.SearchConfig(
        **search_config_in.model_dump(exclude={"source_websites"}),
        source_websites=source_websites_models,
    )
    use_case = UpdateSearchConfigUseCase(repos["search_config_repo"], repos["user_repo"])
    try:
        updated_config = use_case.execute(search_config_id, search_config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not updated_config:
        raise HTTPException(status_code=404, detail="Search config not found")
    return updated_config


@router.delete("/{search_config_id}", response_model=bool)
def delete_search_config(
    search_config_id: int,
    repos=Depends(get_repos),
    current_user: UserEntity = Depends(get_current_active_user),
):
    use_case = DeleteSearchConfigUseCase(repos["search_config_repo"])
    if not GetSearchConfigUseCase(repos["search_config_repo"]).execute(search_config_id):
        raise HTTPException(status_code=404, detail="Search config not found")
    return use_case.execute(search_config_id)


@router.delete("/bulk/", response_model=dict)
def bulk_delete_search_configs(
    ids: list[int] = Body(..., embed=True, description="Lista de IDs para deletar"),
    repos=Depends(get_repos),
    current_user: UserEntity = Depends(get_current_active_user),
):
    use_case = DeleteSearchConfigUseCase(repos["search_config_repo"])
    get_use_case = GetSearchConfigUseCase(repos["search_config_repo"])
    not_found = []
    deleted = []
    for sc_id in ids:
        if get_use_case.execute(sc_id):
            use_case.execute(sc_id)
            deleted.append(sc_id)
        else:
            not_found.append(sc_id)
    return {
        "deleted": deleted,
        "not_found": not_found,
        "message": f"{len(deleted)} configs deletados, {len(not_found)} não encontrados."
    }


@router.get("/users/{user_id}/", response_model=List[SearchConfig])
def read_user_search_configs(
    user_id: int,
    repos=Depends(get_repos),
    current_user: UserEntity = Depends(get_current_active_user),
):
    use_case = GetSearchConfigsByUserUseCase(repos["search_config_repo"], repos["user_repo"])
    try:
        return use_case.execute(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/source_websites/{source_website_id}/", response_model=List[SearchConfig])
def read_website_search_configs(
    source_website_id: int,
    repos=Depends(get_repos),
    current_user: UserEntity = Depends(get_current_active_user),
):
    db_source_website = repos["source_website_repo"].get_by_id(source_website_id)
    if not db_source_website:
        raise HTTPException(status_code=404, detail="Source website not found")
    use_case = GetSearchConfigsBySourceWebsiteUseCase(repos["search_config_repo"])
    return use_case.execute(db_source_website)
