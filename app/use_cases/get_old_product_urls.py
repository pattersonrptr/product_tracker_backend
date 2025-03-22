from typing import List
from app.services.product_service import ProductService

class GetOldProductUrls:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self, days: int):
        return self.product_service.get_products_older_than(days)
