"""
Data Access Layer
"""

from sqlalchemy.orm import Session
from app.models.ad_models import Ad

class AdRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_ad(self, url: str, title: str, price: float) -> Ad:
        ad = Ad(url=url, title=title, price=price)
        self.db.add(ad)
        self.db.commit()
        self.db.refresh(ad)
        return ad
