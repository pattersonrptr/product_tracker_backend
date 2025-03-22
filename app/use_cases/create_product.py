"""
Application Layer
"""

from app.services.product_service import ProductService

class CreateProduct:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self, product_data: dict):
        return self.product_service.create_product(product_data)
