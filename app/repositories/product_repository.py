"""
Data Access Layer
"""
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.product_models import Product
from datetime import datetime, UTC
from decimal import Decimal


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, product_data: dict):
        product = Product(**product_data)
        try:
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception as e:
            self.db.rollback()
            raise e

    def get_all(self):
        products = self.db.query(Product).all()
        for product in products:
            if isinstance(product.price, Decimal):
                product.price = float(product.price)
        return products

    def get_by_id(self, product_id: int):
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product and isinstance(product.price, Decimal):
            product.price = float(product.price)
        return product

    def get_by_url(self, url):
        product = self.db.query(Product).filter(Product.url == url).first()
        if product and isinstance(product.price, Decimal):
            product.price = float(product.price)
        return product

    def get_products_older_than(self, cutoff_date: datetime):
        products = self.db.query(Product).filter(Product.updated_at < cutoff_date).all()
        for product in products:
            if isinstance(product.price, Decimal):
                product.price = float(product.price)
        return products

    def update(self, product_id: int, product_data: dict):
        product = self.get_by_id(product_id)
        if not product:
            return None
        try:
            for key, value in product_data.items():
                setattr(product, key, value)
            product.updated_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(product)
            if isinstance(product.price, Decimal):
                product.price = float(product.price)
            return product
        except Exception as e:
            self.db.rollback()
            raise e

    def update_by_url(self, url: str, product_data: dict):
        product = self.get_by_url(url)
        if not product:
            return None
        try:
            for key, value in product_data.items():
                setattr(product, key, value)
            product.updated_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(product)
            if isinstance(product.price, Decimal):
                product.price = float(product.price)
            return product
        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, product_id: int):
        product = self.get_by_id(product_id)
        if not product:
            return None
        try:
            self.db.delete(product)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def search_products(self, query: str):
        products = self.db.query(Product).filter(
            Product.title.ilike(f"%{query}%")
        ).all()

        for product in products:
            if isinstance(product.price, Decimal):
                product.price = float(product.price)
        return products

    def filter_products(self, filter_data: dict):
        query = self.db.query(Product)

        if 'title' in filter_data and filter_data['title']:
            query = query.filter(Product.title.ilike(f"%{filter_data['title']}%"))

        if 'min_price' in filter_data and filter_data['min_price'] is not None:
            query = query.filter(Product.price >= filter_data['min_price'])

        if 'max_price' in filter_data and filter_data['max_price'] is not None:
            query = query.filter(Product.price <= filter_data['max_price'])

        if 'created_after' in filter_data and filter_data['created_after'] is not None:
            query = query.filter(Product.created_at >= filter_data['created_after'])

        if 'created_before' in filter_data and filter_data['created_before'] is not None:
            query = query.filter(Product.created_at <= filter_data['created_before'])

        products = query.all()
        for product in products:
            if isinstance(product.price, Decimal):
                product.price = float(product.price)
        return products

    def get_product_stats(self):
        stats = self.db.query(
            func.count(Product.id).label("total_products"),
            func.avg(Product.price).label("average_price"),
            func.min(Product.price).label("min_price"),
            func.max(Product.price).label("max_price")
        ).first()

        return {
            "total_products": stats.total_products,
            "average_price": float(stats.average_price) if stats.average_price else 0.0,
            "min_price": float(stats.min_price) if stats.min_price else 0.0,
            "max_price": float(stats.max_price) if stats.max_price else 0.0,
        }

    def get_minimal_products(self):
        products = self.db.query(Product.id, Product.title, Product.price).all()
        return [
            {"id": product.id, "title": product.title, "price": float(product.price)}
            for product in products
        ]
