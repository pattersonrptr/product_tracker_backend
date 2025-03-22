from app.services.product_service import ProductService

class UpdateProduct:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self, product_id: int, product_data: dict):
        return self.product_service.update_product(product_id, product_data)
