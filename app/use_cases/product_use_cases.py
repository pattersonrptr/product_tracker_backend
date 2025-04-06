"""
Application Layer
"""

from app.services.product_service import ProductService
from sqlalchemy.orm import Query
from app.schemas.product_schema import ProductPartialResponse


class CreateProduct:
    def __init__(self, product_service):
        self.product_service = product_service

    def execute(self, product_data):
        product = self.product_service.create_product(product_data)
        return product


class DeleteProduct:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self, product_id: int):
        return self.product_service.delete_product(product_id)


class GetProductById:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self, product_id: int):
        return self.product_service.get_product_by_id(product_id)


class UpdateProduct:
    def __init__(self, product_service):
        self.product_service = product_service

    def execute(self, product_id, update_data):
        product = self.product_service.get_product_by_id(product_id)
        if not product:
            return None

        attributes = update_data.get("attributes", {})
        for key, value in attributes.items():
            setattr(product, key, value)

        return self.product_service.update_product(product)


class FilterProducts:
    def __init__(self, product_service):
        self.product_service = product_service

    def execute(self, filters: dict):
        products = self.product_service.filter_products(filters)
        return [ProductPartialResponse.from_orm(product) for product in products]


class SearchProducts:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self, query: str):
        return self.product_service.search_products(query)


class GetProductStats:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self):
        return self.product_service.get_product_stats()


class GetMinimalProducts:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self):
        return self.product_service.get_minimal_products()
