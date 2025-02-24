from fastapi import APIRouter, Depends
from app.schemas.ad_schema import AdCreate
from app.use_cases.create_ad import CreateAd
from app.services.ad_service import AdService
from app.repositories.ad_repository import AdRepository
from sqlalchemy.orm import Session
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

@router.post("/ads/")
async def create_ad(ad_data: AdCreate, ad_service: AdService = Depends(get_ad_service)):
    return await CreateAd(ad_service).execute(ad_data.dict())
