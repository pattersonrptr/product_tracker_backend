from typing import List, Optional

from app.entities.product import Product
from app.interfaces.repositories.product_repository import ProductRepositoryInterface


class CreateProductUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, product: Product) -> Product:
        # Aqui poderíamos adicionar lógica de negócios antes de criar o produto,
        # como validações complexas ou enriquecimento de dados específicas da API.
        # Por exemplo, verificar se já existe um produto com a mesma URL.
        existing_product = self.product_repository.get_by_url(product.url)
        if existing_product:
            # Decidir o que fazer se o produto já existe: atualizar? ignorar?
            # Por enquanto, vamos apenas retornar o produto existente.
            return existing_product
        return self.product_repository.create(product)


class GetProductByIdUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, product_id: int) -> Optional[Product]:
        return self.product_repository.get_by_id(product_id)


class GetProductByUrlUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, url: str) -> Optional[Product]:
        return self.product_repository.get_by_url(url)


class ListProductsUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self) -> List[Product]:
        return self.product_repository.get_all()


class UpdateProductUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, product_id: int, product: Product) -> Optional[Product]:
        # Aqui poderíamos adicionar lógica de negócios antes de atualizar o produto.
        return self.product_repository.update(product_id, product)


class DeleteProductUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, product_id: int) -> bool:
        # Aqui poderíamos adicionar lógica de negócios antes de deletar o produto.
        return self.product_repository.delete(product_id)


class SearchProductsUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, query: str) -> List[Product]:
        return self.product_repository.search_products(query)


class FilterProductsUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, filter_data: dict) -> List[Product]:
        return self.product_repository.filter_products(filter_data)


class GetProductStatsUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self) -> dict:
        return self.product_repository.get_product_stats()


class GetMinimalProductsUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self) -> List[dict]:
        return self.product_repository.get_minimal_products()
