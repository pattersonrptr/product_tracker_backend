from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy import func, cast, Date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import inspect
from sqlalchemy.types import Boolean

from src.app.infrastructure.database.models.product_model import (
    Product as ProductModel,
)
from src.app.infrastructure.database.models.price_history_model import (
    PriceHistory as PriceHistoryModel,
)
from src.app.entities.product import Product as ProductEntity
from src.app.interfaces.repositories.product_repository import (
    ProductRepositoryInterface,
)


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

    def get_all(
        self,
        column_filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Tuple[List[ProductEntity], int]:
        query = self.db.query(ProductModel)

        if column_filters:
            for field, filter_info in column_filters.items():
                value = filter_info.get("value")
                operator = filter_info.get("operator", "equals")

                column = getattr(ProductModel, field, None)
                if column is None:
                    print(f"Warning: Filter field '{field}' not found on ProductModel.")
                    continue

                column_type = (
                    inspect(column).type if hasattr(inspect(column), "type") else None
                )

                # Support for date filters
                if field in ["created_at", "updated_at"]:
                    # Convert ISO string to datetime.date if necessary
                    if value and isinstance(value, str):
                        try:
                            value = datetime.fromisoformat(
                                value.replace("Z", "+00:00")
                            ).date()
                        except Exception:
                            print("Unable to convert value to date:", value)
                            pass
                    if isinstance(value, datetime):
                        value = value.date()

                    if operator in ["is"]:
                        query = query.filter(cast(column, Date) == value)
                    elif operator in ["not"]:
                        query = query.filter(cast(column, Date) != value)
                    elif operator in ["after"]:
                        query = query.filter(cast(column, Date) > value)
                    elif operator in ["onOrAfter"]:
                        query = query.filter(cast(column, Date) >= value)
                    elif operator in ["before"]:
                        query = query.filter(cast(column, Date) < value)
                    elif operator in ["onOrBefore"]:
                        query = query.filter(cast(column, Date) <= value)
                    elif operator in ["isEmpty"]:
                        query = query.filter(column.is_(None))
                    elif operator in ["isNotEmpty"]:
                        query = query.filter(column.isnot(None))
                    continue

                if value is None:
                    if operator == "isEmpty":
                        query = query.filter(column.is_(None) | (column == ""))
                    elif operator == "isNotEmpty":
                        query = query.filter(column.isnot(None) & (column != ""))
                    continue

                if isinstance(column_type, Boolean):
                    if operator == "equals" or operator == "is":
                        query = query.filter(column == value)
                    elif operator == "notEquals":
                        query = query.filter(column != value)
                else:
                    if operator == "equals":
                        query = query.filter(column == value)
                    elif operator == "notEquals":
                        query = query.filter(column != value)
                    elif operator == "contains":
                        if hasattr(column, "ilike"):
                            query = query.filter(column.ilike(f"%{value}%"))
                        else:
                            query = query.filter(column.contains(value))
                    elif operator == "notContains":
                        if hasattr(column, "ilike"):
                            query = query.filter(~column.ilike(f"%{value}%"))
                        else:
                            query = query.filter(~column.contains(value))
                    elif operator == "startsWith":
                        if hasattr(column, "ilike"):
                            query = query.filter(column.ilike(f"{value}%"))
                        else:
                            query = query.filter(column.startswith(value))
                    elif operator == "endsWith":
                        if hasattr(column, "ilike"):
                            query = query.filter(column.ilike(f"%{value}"))
                        else:
                            query = query.filter(column.endswith(value))

        if sort_by:
            sort_column = getattr(ProductModel, sort_by, None)
            if sort_column:
                if sort_order == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())

        total_count = query.count()
        db_products = (
            query.options(joinedload(ProductModel.price_history))
            .limit(limit)
            .offset(offset)
            .all()
        )
        products = []

        for db_product in db_products:
            product_entity = ProductEntity(**db_product.__dict__)
            if db_product.price_history:
                product_entity.current_price = db_product.price_history[-1].price
            products.append(product_entity)

        return products, total_count

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
                db_product.updated_at = datetime.now(timezone.utc)
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

    def search_products(
        self, query: str, limit: int, offset: int
    ) -> List[ProductEntity]:
        db_products = (
            self.db.query(ProductModel)
            .options(joinedload(ProductModel.price_history))
            .filter(ProductModel.title.ilike(f"%{query}%"))
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [ProductEntity(**db_product.__dict__) for db_product in db_products]

    def filter_products(
        self, filter_data: Dict, limit: int, offset: int
    ) -> List[ProductEntity]:
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

        if "created_after" in filter_data and filter_data["created_after"]:
            query = query.filter(
                ProductModel.created_at >= filter_data["created_after"]
            )

        if "created_before" in filter_data and filter_data["created_before"]:
            query = query.filter(
                ProductModel.created_at <= filter_data["created_before"]
            )

        if "updated_after" in filter_data and filter_data["updated_after"]:
            query = query.filter(
                ProductModel.updated_at >= filter_data["updated_after"]
            )

        if "updated_before" in filter_data and filter_data["updated_before"]:
            query = query.filter(
                ProductModel.updated_at <= filter_data["updated_before"]
            )

        db_products = query.limit(limit).offset(offset).all()
        products = []

        for db_product in db_products:
            product_entity = ProductEntity(**db_product.__dict__)
            if db_product.price_history:
                product_entity.current_price = db_product.price_history[-1].price
            products.append(product_entity)
        return products
        # return [ProductEntity(**db_product.__dict__) for db_product in db_products]

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

    def get_minimal_products(self, limit: int, offset: int) -> List[dict]:
        db_products = (
            self.db.query(ProductModel)
            .options(joinedload(ProductModel.price_history))
            .limit(limit)
            .offset(offset)
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
