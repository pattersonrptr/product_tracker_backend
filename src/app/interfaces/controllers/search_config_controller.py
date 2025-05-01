from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.entities import search_config as SearchConfigEntity
from src.app.use_cases.search_config_use_cases import SearchConfigUseCases
from src.app.interfaces.schemas.search_config_schema import (
    SearchConfig,
    SearchConfigCreate,
    SearchConfigUpdate,
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


def get_search_config_use_cases(db: Session = Depends(get_db)):
    search_config_repo = SearchConfigRepository(db)
    user_repo = UserRepository(db)
    return SearchConfigUseCases(search_config_repo, user_repo)


@router.post("/", response_model=SearchConfig, status_code=201)
def create_search_config(
    search_config_in: SearchConfigCreate,
    use_cases: SearchConfigUseCases = Depends(get_search_config_use_cases),
):
    source_websites = []
    if search_config_in.source_websites:
        source_website_repo = SourceWebsiteRepository(use_cases.search_config_repo.db)
        for sw_id in search_config_in.source_websites:
            db_sw = source_website_repo.get_by_id(sw_id)
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
    return use_cases.create_search_config(search_config)


@router.get("/", response_model=List[SearchConfig])
def read_search_configs(
    use_cases: SearchConfigUseCases = Depends(get_search_config_use_cases),
):
    return use_cases.get_all_search_configs()


@router.get("/{search_config_id}", response_model=SearchConfig)
def read_search_config(
    search_config_id: int,
    use_cases: SearchConfigUseCases = Depends(get_search_config_use_cases),
):
    search_config = use_cases.get_search_config(search_config_id)
    if not search_config:
        raise HTTPException(status_code=404, detail="Search config not found")
    return search_config


@router.put("/{search_config_id}", response_model=SearchConfig)
def update_search_config(
    search_config_id: int,
    search_config_in: SearchConfigUpdate,
    use_cases: SearchConfigUseCases = Depends(get_search_config_use_cases),
):
    source_websites_models = []
    if search_config_in.source_websites:
        source_website_repo = SourceWebsiteRepository(use_cases.search_config_repo.db)
        for sw_id in search_config_in.source_websites:
            db_sw = source_website_repo.get_by_id(sw_id)
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
    updated_config = use_cases.update_search_config(search_config_id, search_config)
    if not updated_config:
        raise HTTPException(status_code=404, detail="Search config not found")
    return updated_config


@router.delete("/{search_config_id}", response_model=bool)
def delete_search_config(
    search_config_id: int,
    use_cases: SearchConfigUseCases = Depends(get_search_config_use_cases),
):
    if not use_cases.get_search_config(search_config_id):
        raise HTTPException(status_code=404, detail="Search config not found")
    return use_cases.delete_search_config(search_config_id)


@router.get("/users/{user_id}/", response_model=List[SearchConfig])
def read_user_search_configs(
    user_id: int, use_cases: SearchConfigUseCases = Depends(get_search_config_use_cases)
):
    try:
        return use_cases.get_search_configs_by_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/source_websites/{source_website_id}/", response_model=List[SearchConfig])
def read_website_search_configs(
    source_website_id: int,
    use_cases: SearchConfigUseCases = Depends(get_search_config_use_cases),
):
    source_website_repo = SourceWebsiteRepository(use_cases.search_config_repo.db)
    db_source_website = source_website_repo.get_by_id(source_website_id)
    if not db_source_website:
        raise HTTPException(status_code=404, detail="Source website not found")
    return use_cases.get_search_configs_by_source_website(db_source_website)
