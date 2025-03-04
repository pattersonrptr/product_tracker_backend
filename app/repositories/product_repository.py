"""
Data Access Layer
"""

from sqlalchemy.orm import Session
from app.models.product_models import Product

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, product_data: dict):
        product = Product(**product_data)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_all(self):
        return self.db.query(Product).all()

    def get_by_id(self, product_id: int):
        return self.db.query(Product).filter(Product.id == product_id).first()

    def update(self, product_id: int, product_data: dict):
        product = self.get_by_id(product_id)
        if not product:
            return None
        for key, value in product_data.items():
            setattr(product, key, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: int):
        product = self.get_by_id(product_id)
        if not product:
            return None
        self.db.delete(product)
        self.db.commit()
        return True
