"""
Data Access Layer
"""

from sqlalchemy.orm import Session
from app.models.ad_models import Ad

class AdRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, ad_data: dict):
        ad = Ad(**ad_data)
        self.db.add(ad)
        self.db.commit()
        self.db.refresh(ad)
        return ad

    def get_all(self):
        return self.db.query(Ad).all()

    def get_by_id(self, ad_id: int):
        return self.db.query(Ad).filter(Ad.id == ad_id).first()

    def update(self, ad_id: int, ad_data: dict):
        ad = self.get_by_id(ad_id)
        if not ad:
            return None
        for key, value in ad_data.items():
            setattr(ad, key, value)
        self.db.commit()
        self.db.refresh(ad)
        return ad

    def delete(self, ad_id: int):
        ad = self.get_by_id(ad_id)
        if not ad:
            return None
        self.db.delete(ad)
        self.db.commit()
        return True
