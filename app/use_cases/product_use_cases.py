"""
Application Layer
"""

from app.services.product_service import ProductService

class CreateProduct:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self, product_data: dict):
        return self.product_service.create_product(product_data)

class DeleteProduct:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self, product_id: int):
        return self.product_service.delete_product(product_id)

# class GetOldProductUrls:
#     def __init__(self, product_service: ProductService):
#         self.product_service = product_service
#
#     def execute(self, days: int):
#         return self.product_service.get_products_older_than(days)

class GetProductById:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self, product_id: int):
        return self.product_service.get_product_by_id(product_id)

# class GetProductByUrl:
#     def __init__(self, product_service: ProductService):
#         self.product_service = product_service
#
#     def execute(self, url: str):
#         return self.product_service.get_product_by_url(url)

# class GetProducts:
#     def __init__(self, product_service: ProductService):
#         self.product_service = product_service
#
#     def execute(self, url: str = None):
#         if url:
#             return self.product_service.get_product_by_url(url)
#         return self.product_service.get_all_products()

class UpdateProduct:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self, product_id: int, product_data: dict):
        return self.product_service.update_product(product_id, product_data)

# class UpdateProductByUrl:
#     def __init__(self, product_service: ProductService):
#         self.product_service = product_service
#
#     def execute(self, url: str, product_data: dict):
#         return self.product_service.update_product_by_url(url, product_data)

class FilterProducts:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self, filter_data: dict):
        return self.product_service.filter_products(filter_data)

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