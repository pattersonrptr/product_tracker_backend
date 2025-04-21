from typing import Optional, List

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.infrastructure.database.models.product_model import (
    Product as ProductModel,
)
from app.infrastructure.database.models.price_history_model import (
    PriceHistory as PriceHistoryModel,
)
from app.entities.product import product as ProductEntity
from app.interfaces.repositories.product_repository import ProductRepositoryInterface

import logging

logging.basicConfig(level=logging.INFO)


class ProductRepository(ProductRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def create(self, product: ProductEntity.Product) -> ProductEntity.Product:
        logging.info(f"Tipo da variável 'product' no repository: {type(product)}")
        logging.info(f"Conteúdo da variável 'product' no repository: {product}")
        try:
            db_product = ProductModel(
                **product.__dict__
            )  # Crie um model SQLAlchemy a partir da entidade
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)
            return ProductEntity.Product(
                **db_product.__dict__
            )  # Retorne uma entidade pura
        except Exception as e:
            self.db.rollback()
            raise e

    def get_all(self) -> List[ProductEntity.Product]:
        db_products = (
            self.db.query(ProductModel)  # Use o model SQLAlchemy
            .options(joinedload(ProductModel.price_history))
            .all()
        )
        return [
            ProductEntity.Product(**db_product.__dict__) for db_product in db_products
        ]  # Converta para entidades

    def get_by_id(self, product_id: int) -> Optional[ProductEntity.Product]:
        db_product = (
            self.db.query(ProductModel)  # Use o model SQLAlchemy
            .options(joinedload(ProductModel.price_history))
            .filter(ProductModel.id == product_id)
            .first()
        )
        return (
            ProductEntity.Product(**db_product.__dict__) if db_product else None
        )  # Converta para entidade

    def get_by_url(self, url: str) -> Optional[ProductEntity.Product]:
        db_product = (
            self.db.query(ProductModel)  # Use o model SQLAlchemy
            .options(joinedload(ProductModel.price_history))
            .filter(ProductModel.url == url)
            .first()
        )
        return (
            ProductEntity.Product(**db_product.__dict__) if db_product else None
        )  # Converta para entidade

    def update(
        self, product_id: int, product: ProductEntity.Product
    ) -> Optional[ProductEntity.Product]:
        try:
            db_product = (
                self.db.query(ProductModel)
                .filter(ProductModel.id == product_id)
                .first()
            )
            if db_product:
                logging.info(
                    f"Tipo de db_product ANTES da atualização: {type(db_product)}"
                )
                logging.info(
                    f"Conteúdo de db_product ANTES da atualização: {db_product.__dict__}"
                )
                for key, value in product.__dict__.items():
                    if hasattr(db_product, key):
                        setattr(db_product, key, value)
                self.db.commit()
                logging.info(f"Tipo de db_product ANTES do refresh: {type(db_product)}")
                logging.info(
                    f"Conteúdo de db_product ANTES do refresh: {db_product.__dict__}"
                )
                self.db.refresh(db_product)
                logging.info(f"Tipo de db_product APÓS o refresh: {type(db_product)}")
                logging.info(
                    f"Conteúdo de db_product APÓS o refresh: {db_product.__dict__}"
                )
                return ProductEntity.Product(**db_product.__dict__)
            return None
        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, product_id: int) -> bool:
        db_product = (
            self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        )  # Use o model SQLAlchemy
        if not db_product:
            return False
        try:
            self.db.delete(db_product)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def search_products(self, query: str) -> List[ProductEntity.Product]:
        db_products = (
            self.db.query(ProductModel)  # Use o model SQLAlchemy
            .options(joinedload(ProductModel.price_history))
            .filter(ProductModel.title.ilike(f"%{query}%"))
            .all()
        )
        return [
            ProductEntity.Product(**db_product.__dict__) for db_product in db_products
        ]  # Converta para entidades

    def filter_products(self, filter_data: dict) -> List[ProductEntity.Product]:
        query = self.db.query(ProductModel).options(
            joinedload(ProductModel.price_history)
        )  # Use o model SQLAlchemy

        if "url" in filter_data and filter_data["url"]:
            query = query.filter(ProductModel.url.ilike(f"%{filter_data['url']}%"))

        if "title" in filter_data and filter_data["title"]:
            query = query.filter(ProductModel.title.ilike(f"%{filter_data['title']}%"))

        # Adapte os filtros de preço para não usar mais Product.price diretamente
        # Agora o preço "atual" está em product.price_history[-1].price
        # Isso exigiria joins com PriceHistoryModel e subqueries para filtrar pelo preço atual

        if (
            "min_current_price" in filter_data
            and filter_data["min_current_price"] is not None
        ):
            # Implemente a lógica de filtragem pelo preço atual usando joins/subqueries
            pass

        if (
            "max_current_price" in filter_data
            and filter_data["max_current_price"] is not None
        ):
            # Implemente a lógica de filtragem pelo preço atual usando joins/subqueries
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
        return [
            ProductEntity.Product(**db_product.__dict__) for db_product in db_products
        ]  # Converta para entidades

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
            self.db.query(ProductModel)  # Use o model SQLAlchemy
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
