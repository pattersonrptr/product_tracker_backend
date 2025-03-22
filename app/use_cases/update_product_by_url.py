from app.services.product_service import ProductService

class UpdateProductByUrl:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self, url: str, product_data: dict):
        return self.product_service.update_product_by_url(url, product_data)
