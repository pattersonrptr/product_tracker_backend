from typing import Optional, List

# from app.entities.product import Product
from app.entities.product.price_history import PriceHistory as PriceHistoryEntity
from app.interfaces.repositories.product_repository import ProductRepositoryInterface
from app.interfaces.repositories.price_history_repository import (
    PriceHistoryRepositoryInterface,
)
from app.interfaces.schemas.product_schema import ProductUpdate
from app.entities.product.product import Product as ProductEntity

import logging

logging.basicConfig(level=logging.INFO)


class CreateProductUseCase:
    def __init__(
        self,
        product_repository: ProductRepositoryInterface,
        price_history_repository: PriceHistoryRepositoryInterface,
    ):
        self.product_repository = product_repository
        self.price_history_repository = price_history_repository

    def execute(self, product: ProductEntity, initial_price: float):
        logging.info(f"Tipo da variável 'product' no use case: {type(product)}")
        logging.info(
            f"Conteúdo da variável 'product' no use case: {product.__dict__ if hasattr(product, '__dict__') else product}"
        )
        created_product = self.product_repository.create(product)

        if created_product is not None and initial_price is not None:
            price_history_entry = PriceHistoryEntity(
                product_id=created_product.id, price=initial_price
            )
            self.price_history_repository.create(price_history_entry)

            retrieved_product = self.product_repository.get_by_id(created_product.id)
            return retrieved_product
        return created_product


class GetProductByIdUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, product_id: int) -> Optional[ProductEntity]:
        return self.product_repository.get_by_id(product_id)


class GetProductByUrlUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, url: str) -> Optional[ProductEntity]:
        return self.product_repository.get_by_url(url)


class ListProductsUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self) -> List[ProductEntity]:
        return self.product_repository.get_all()


class UpdateProductUseCase:
    def __init__(
        self,
        product_repository: ProductRepositoryInterface,
        price_history_repository: PriceHistoryRepositoryInterface,
    ):
        self.product_repository = product_repository
        self.price_history_repository = price_history_repository

    def execute(
        self,
        product_id: int,
        product_update: ProductUpdate,
        new_price: Optional[float] = None,
    ) -> Optional[ProductEntity]:
        existing_product = self.product_repository.get_by_id(product_id)

        if not existing_product:
            return None

        for key, value in product_update.model_dump(
            exclude={"price"}, exclude_unset=True
        ).items():
            setattr(existing_product, key, value)

        updated_product = self.product_repository.update(product_id, existing_product)

        if updated_product is not None and new_price is not None:
            price_history_entry = PriceHistoryEntity(
                product_id=updated_product.id, price=new_price
            )
            self.price_history_repository.create(price_history_entry)

        return updated_product


class DeleteProductUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, product_id: int) -> bool:
        return self.product_repository.delete(product_id)


class SearchProductsUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, query: str) -> List[ProductEntity]:
        return self.product_repository.search_products(query)


class FilterProductsUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, filter_data: dict) -> List[ProductEntity]:
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
