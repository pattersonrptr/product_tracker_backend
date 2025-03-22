from app.services.product_service import ProductService

class GetProductByUrl:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def execute(self, url: str):
        return self.product_service.get_product_by_url(url)
