from datetime import UTC, datetime, timedelta
from decimal import Decimal

from pydantic import HttpUrl

from app.models import Product
from app.repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def create_product(self, product_data: dict):
        if isinstance(product_data.get('url'), HttpUrl):
            product_data['url'] = str(product_data['url'])
        return self.repository.create(product_data)

    def get_all_products(self):
        products = self.repository.get_all() or []
        return products

    def get_product_by_id(self, product_id: int):
        product = self.repository.get_by_id(product_id)
        return product

    def get_product_by_url(self, url):
        product = self.repository.get_by_url(url) or []
        return product

    # def get_products_older_than(self, days: int):
    #     cutoff_date = datetime.now(UTC) - timedelta(days=days)
    #     products = self.repository.get_products_older_than(cutoff_date) or []
    #     return products

    def update_product(self, product_id: int, product_data: dict):
        if 'url' in product_data and isinstance(product_data['url'], HttpUrl):
            product_data['url'] = str(product_data['url'])
        return self.repository.update(product_id, product_data)

    # def update_product_by_url(self, url: str, product_data: dict):
    #     if 'url' in product_data and isinstance(product_data['url'], HttpUrl):
    #         product_data['url'] = str(product_data['url'])
    #     return self.repository.update_by_url(url, product_data)

    def delete_product(self, product_id: int):
        return self.repository.delete(product_id)

    def filter_products(self, filter_data: dict):
        return self.repository.filter_products(filter_data)

    def search_products(self, query: str):
        return self.repository.search_products(query)

    def get_product_stats(self):
        return self.repository.get_product_stats()

    def get_minimal_products(self):
        return self.repository.get_minimal_products()
