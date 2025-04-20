from datetime import UTC, datetime
from typing import Optional, List

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.entities.product import Product
from app.entities.product.price_history import PriceHistory
from app.interfaces.repositories.product_repository import ProductRepositoryInterface


class ProductRepository(ProductRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:
        try:
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception as e:
            self.db.rollback()
            raise e

    def get_all(self) -> List[Product]:
        return self.db.query(Product).options(joinedload(Product.price_history)).all()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return (
            self.db.query(Product)
            .options(joinedload(Product.price_history))
            .filter(Product.id == product_id)
            .first()
        )

    def get_by_url(self, url: str) -> Optional[Product]:
        return (
            self.db.query(Product)
            .options(joinedload(Product.price_history))
            .filter(Product.url == url)
            .first()
        )

    def update(self, product_id: int, product: Product) -> Optional[Product]:
        db_product = self.get_by_id(product_id)
        if not db_product:
            return None
        try:
            for key, value in product.__dict__.items():
                if key not in ["id", "created_at"]:
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
        return (
            self.db.query(Product)
            .options(joinedload(Product.price_history))
            .filter(Product.title.ilike(f"%{query}%"))
            .all()
        )

    def filter_products(self, filter_data: dict) -> List[Product]:
        query = self.db.query(Product).options(joinedload(Product.price_history))

        if "url" in filter_data and filter_data["url"]:
            query = query.filter(Product.url.ilike(f"%{filter_data['url']}%"))

        if "title" in filter_data and filter_data["title"]:
            query = query.filter(Product.title.ilike(f"%{filter_data['title']}%"))

        # Adapte os filtros de preço para não usar mais Product.price diretamente, se necessário
        # Agora o preço "atual" está em product.price_history[-1].price

        # Exemplo de como você poderia filtrar por um certo intervalo do preço *atual*:
        if (
            "min_current_price" in filter_data
            and filter_data["min_current_price"] is not None
        ):
            # Isso exigiria uma subquery ou uma forma mais complexa de filtrar
            pass  # Implemente a lógica de filtragem pelo preço atual aqui

        if (
            "max_current_price" in filter_data
            and filter_data["max_current_price"] is not None
        ):
            # Isso exigiria uma subquery ou uma forma mais complexa de filtrar
            pass  # Implemente a lógica de filtragem pelo preço atual aqui

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
        # Subquery para obter o preço mais recente de cada produto
        subquery = (
            self.db.query(
                PriceHistory.product_id,
                func.max(PriceHistory.created_at).label("latest_created_at"),
            )
            .group_by(PriceHistory.product_id)
            .subquery()
        )

        latest_prices_subquery = (
            self.db.query(PriceHistory.price)
            .join(
                subquery,
                (PriceHistory.product_id == subquery.c.product_id)
                & (PriceHistory.created_at == subquery.c.latest_created_at),
            )
            .subquery()
        )

        total_products = self.db.query(func.count(Product.id)).scalar()

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
        products = (
            self.db.query(Product).options(joinedload(Product.price_history)).all()
        )
        minimal_products_list = []
        for product in products:
            current_price = None
            if product.price_history:
                current_price = product.price_history[-1].price
            minimal_products_list.append(
                {
                    "id": product.id,
                    "title": product.title,
                    "url": product.url,
                    "current_price": float(current_price)
                    if current_price is not None
                    else None,
                }
            )
        return minimal_products_list
