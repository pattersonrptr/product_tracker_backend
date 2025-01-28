from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.ad import Ad
from app.db.session import get_db

router = APIRouter()

@router.get("/ads/", response_model=list[Ad])
def read_ads(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Ad).offset(skip).limit(limit).all()
