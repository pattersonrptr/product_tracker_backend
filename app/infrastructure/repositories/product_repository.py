from datetime import UTC, datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.entities.product import Product
from app.interfaces.repositories.product_repository import ProductRepositoryInterface


class ProductRepository(ProductRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:  # Recebe objeto Product
        try:
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception as e:
            self.db.rollback()
            raise e

    def get_all(self) -> List[Product]:
        products = self.db.query(Product).all()
        return products

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_url(self, url: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.url == url).first()

    def update(
        self, product_id: int, product: Product
    ) -> Optional[Product]:  # Recebe objeto Product
        db_product = self.get_by_id(product_id)
        if not db_product:
            return None
        try:
            for key, value in product.__dict__.items():
                if key not in [
                    "id",
                    "created_at",
                ]:  # Evita sobrescrever campos importantes
                    setattr(db_product, key, value)
            db_product.updated_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(db_product)
            return db_product
        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, product_id: int) -> bool:
        db_product = self.get_by_id(product_id)
        if not db_product:
            return False
        try:
            self.db.delete(db_product)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def search_products(self, query: str) -> List[Product]:
        return self.db.query(Product).filter(Product.title.ilike(f"%{query}%")).all()

    def filter_products(self, filter_data: dict) -> List[Product]:
        query = self.db.query(Product)

        if "url" in filter_data and filter_data["url"]:
            query = query.filter(Product.url.ilike(f"%{filter_data['url']}%"))

        if "title" in filter_data and filter_data["title"]:
            query = query.filter(Product.title.ilike(f"%{filter_data['title']}%"))

        if "min_price" in filter_data and filter_data["min_price"] is not None:
            query = query.filter(Product.price >= filter_data["min_price"])

        if "max_price" in filter_data and filter_data["max_price"] is not None:
            query = query.filter(Product.price <= filter_data["max_price"])

        if "created_after" in filter_data and filter_data["created_after"] is not None:
            query = query.filter(Product.created_at >= filter_data["created_after"])

        if (
            "created_before" in filter_data
            and filter_data["created_before"] is not None
        ):
            query = query.filter(Product.created_at <= filter_data["created_before"])

        if "updated_after" in filter_data and filter_data["updated_after"] is not None:
            query = query.filter(Product.updated_at >= filter_data["updated_after"])

        if (
            "updated_before" in filter_data
            and filter_data["updated_before"] is not None
        ):
            query = query.filter(Product.updated_at <= filter_data["updated_before"])

        return query.all()

    def get_product_stats(self) -> dict:
        stats = self.db.query(
            func.count(Product.id).label("total_products"),
            func.avg(Product.price).label("average_price"),
            func.min(Product.price).label("min_price"),
            func.max(Product.price).label("max_price"),
        ).first()

        return {
            "total_products": stats.total_products,
            "average_price": float(stats.average_price) if stats.average_price else 0.0,
            "min_price": float(stats.min_price) if stats.min_price else 0.0,
            "max_price": float(stats.max_price) if stats.max_price else 0.0,
        }

    def get_minimal_products(self):  #  -> List[dict]:
        return self.db.query(Product.id, Product.title, Product.price).all()
