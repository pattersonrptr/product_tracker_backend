from app.services.product_service import ProductService

class GetProductById:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self, product_id: int):
        return self.product_service.get_product_by_id(product_id)
