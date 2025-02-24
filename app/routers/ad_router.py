from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from typing import List

from app.schemas.ad_schema import AdCreate, AdResponse
from app.use_cases.create_ad import CreateAd
from app.services.ad_service import AdService
from app.repositories.ad_repository import AdRepository
from app.database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_ad_service(db: Session = Depends(get_db)):
    repository = AdRepository(db)
    return AdService(repository)


@router.post("/ads/", response_model=AdResponse, status_code=status.HTTP_201_CREATED)
async def create_ad(ad_data: AdCreate, ad_service: AdService = Depends(get_ad_service)):
    return await CreateAd(ad_service).execute(ad_data.dict())


@router.get("/ads/", response_model=List[AdResponse])
async def get_ads(ad_service: AdService = Depends(get_ad_service)):
    return await ad_service.get_all_ads()


@router.get("/ads/{ad_id}", response_model=AdResponse)
async def get_ad(ad_id: int, ad_service: AdService = Depends(get_ad_service)):
    ad = await ad_service.get_ad_by_id(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad


@router.put("/ads/{ad_id}", response_model=AdResponse)
async def update_ad(ad_id: int, ad_data: AdCreate, ad_service: AdService = Depends(get_ad_service)):
    updated_ad = await ad_service.update_ad(ad_id, ad_data.dict())
    if not updated_ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return updated_ad


@router.delete("/ads/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad(ad_id: int, ad_service: AdService = Depends(get_ad_service)):
    deleted = await ad_service.delete_ad(ad_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ad not found")
