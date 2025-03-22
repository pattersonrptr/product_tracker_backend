"""
Business Logic Layer
"""
from datetime import datetime, UTC, timedelta
from pydantic import HttpUrl

from app.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def create_product(self, product_data: dict):
        if isinstance(product_data.get('url'), HttpUrl):
            product_data['url'] = str(product_data['url'])
        return self.repository.create(product_data)

    def get_all_products(self):
        return self.repository.get_all() or []

    def get_product_by_id(self, product_id: int):
        return self.repository.get_by_id(product_id)

    def get_product_by_url(self, url):
        return self.repository.get_by_url(url) or []

    def get_products_older_than(self, days: int):
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        return self.repository.get_products_older_than(cutoff_date) or []

    def update_product(self, product_id: int, product_data: dict):
        if 'url' in product_data and isinstance(product_data['url'], HttpUrl):
            product_data['url'] = str(product_data['url'])
        return self.repository.update(product_id, product_data)

    def update_product_by_url(self, url: str, product_data: dict):
        print(f"Updating product with URL: {url}")
        if 'url' in product_data and isinstance(product_data['url'], HttpUrl):
            product_data['url'] = str(product_data['url'])
        return self.repository.update_by_url(url, product_data)

    def delete_product(self, product_id: int):
        return self.repository.delete(product_id)
