from datetime import datetime, UTC
from typing import Optional, List

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.infrastructure.database.models.product_model import (
    Product as ProductModel,
)
from app.infrastructure.database.models.price_history_model import (
    PriceHistory as PriceHistoryModel,
)
from app.entities.product.product import Product as ProductEntity
from app.interfaces.repositories.product_repository import ProductRepositoryInterface


class ProductRepository(ProductRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def create(self, product: ProductEntity) -> ProductEntity:
        try:
            db_product_data = {
                key: value
                for key, value in product.__dict__.items()
                if key != "current_price"
            }
            db_product = ProductModel(**db_product_data)
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)
            return ProductEntity(**db_product.__dict__)
        except Exception as e:
            self.db.rollback()
            raise e

    def get_all(self) -> List[ProductEntity]:
        db_products = (
            self.db.query(ProductModel)
            .options(joinedload(ProductModel.price_history))
            .all()
        )
        products = []
        for db_product in db_products:
            product_entity = ProductEntity(**db_product.__dict__)
            if db_product.price_history:
                product_entity.current_price = db_product.price_history[-1].price
            products.append(product_entity)
        return products

    def get_by_id(self, product_id: int) -> Optional[ProductEntity]:
        db_product = (
            self.db.query(ProductModel)
            .options(joinedload(ProductModel.price_history))
            .filter(ProductModel.id == product_id)
            .first()
        )
        if db_product:
            product_entity = ProductEntity(**db_product.__dict__)
            if db_product.price_history:
                product_entity.current_price = db_product.price_history[-1].price
            return product_entity
        return None

    def get_by_url(self, url: str) -> Optional[ProductEntity]:
        db_product = (
            self.db.query(ProductModel)
            .options(joinedload(ProductModel.price_history))
            .filter(ProductModel.url == url)
            .first()
        )
        if db_product:
            product_entity = ProductEntity(**db_product.__dict__)
            if db_product.price_history:
                product_entity.current_price = db_product.price_history[-1].price
            return product_entity
        return None

    def update(
        self, product_id: int, product: ProductEntity
    ) -> Optional[ProductEntity]:
        try:
            db_product = (
                self.db.query(ProductModel)
                .filter(ProductModel.id == product_id)
                .first()
            )
            if db_product:
                for key, value in product.__dict__.items():
                    if hasattr(db_product, key) and key != "current_price":
                        setattr(db_product, key, value)
                db_product.updated_at = datetime.now(UTC)
                self.db.commit()
                self.db.refresh(db_product)

                return ProductEntity(**db_product.__dict__)
            return None
        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, product_id: int) -> bool:
        db_product = (
            self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        )
        if not db_product:
            return False
        try:
            self.db.delete(db_product)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def search_products(self, query: str) -> List[ProductEntity]:
        db_products = (
            self.db.query(ProductModel)
            .options(joinedload(ProductModel.price_history))
            .filter(ProductModel.title.ilike(f"%{query}%"))
            .all()
        )
        products = []
        for db_product in db_products:
            product_entity = ProductEntity(**db_product.__dict__)
            if db_product.price_history:
                product_entity.current_price = db_product.price_history[-1].price
            products.append(product_entity)
        return products

    def filter_products(self, filter_data: dict) -> List[ProductEntity]:
        query = self.db.query(ProductModel).options(
            joinedload(ProductModel.price_history)
        )

        if "url" in filter_data and filter_data["url"]:
            query = query.filter(ProductModel.url.ilike(f"%{filter_data['url']}%"))

        if "title" in filter_data and filter_data["title"]:
            query = query.filter(ProductModel.title.ilike(f"%{filter_data['title']}%"))

        if (
            "min_current_price" in filter_data
            and filter_data["min_current_price"] is not None
        ):
            pass

        if (
            "max_current_price" in filter_data
            and filter_data["max_current_price"] is not None
        ):
            pass

        if "created_after" in filter_data and filter_data["created_after"] is not None:
            query = query.filter(
                ProductModel.created_at >= filter_data["created_after"]
            )

        if (
            "created_before" in filter_data
            and filter_data["created_before"] is not None
        ):
            query = query.filter(
                ProductModel.created_at <= filter_data["created_before"]
            )

        if "updated_after" in filter_data and filter_data["updated_after"] is not None:
            query = query.filter(
                ProductModel.updated_at >= filter_data["updated_after"]
            )

        if (
            "updated_before" in filter_data
            and filter_data["updated_before"] is not None
        ):
            query = query.filter(
                ProductModel.updated_at <= filter_data["updated_before"]
            )

        db_products = query.all()
        products = []
        for db_product in db_products:
            product_entity = ProductEntity(**db_product.__dict__)
            if db_product.price_history:
                product_entity.current_price = db_product.price_history[-1].price
            products.append(product_entity)
        return products

    def get_product_stats(self) -> dict:
        subquery = (
            self.db.query(
                PriceHistoryModel.product_id,
                func.max(PriceHistoryModel.created_at).label("latest_created_at"),
            )
            .group_by(PriceHistoryModel.product_id)
            .subquery()
        )

        latest_prices_subquery = (
            self.db.query(PriceHistoryModel.price)
            .join(
                subquery,
                (PriceHistoryModel.product_id == subquery.c.product_id)
                & (PriceHistoryModel.created_at == subquery.c.latest_created_at),
            )
            .subquery()
        )

        total_products = self.db.query(func.count(ProductModel.id)).scalar()

        average_price = (
            self.db.query(func.avg(latest_prices_subquery.c.price)).scalar()
            if total_products > 0
            else 0.0
        )
        min_price = (
            self.db.query(func.min(latest_prices_subquery.c.price)).scalar()
            if total_products > 0
            else 0.0
        )
        max_price = (
            self.db.query(func.max(latest_prices_subquery.c.price)).scalar()
            if total_products > 0
            else 0.0
        )

        return {
            "total_products": total_products if total_products is not None else 0,
            "average_price": float(average_price) if average_price is not None else 0.0,
            "min_price": float(min_price) if min_price is not None else 0.0,
            "max_price": float(max_price) if max_price is not None else 0.0,
        }

    def get_minimal_products(self) -> List[dict]:
        db_products = (
            self.db.query(ProductModel)
            .options(joinedload(ProductModel.price_history))
            .all()
        )
        minimal_products_list = []
        for db_product in db_products:
            current_price = None
            if db_product.price_history:
                current_price = db_product.price_history[-1].price
            minimal_products_list.append(
                {
                    "id": db_product.id,
                    "title": db_product.title,
                    "url": db_product.url,
                    "current_price": float(current_price)
                    if current_price is not None
                    else None,
                }
            )
        return minimal_products_list
