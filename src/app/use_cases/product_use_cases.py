from typing import Optional, List, Dict, Any

from src.app.entities.price_history import PriceHistory as PriceHistoryEntity
from src.app.interfaces.repositories.product_repository import (
    ProductRepositoryInterface,
)
from src.app.interfaces.repositories.price_history_repository import (
    PriceHistoryRepositoryInterface,
)
from src.app.interfaces.schemas.product_schema import ProductUpdate
from src.app.entities.product import Product as ProductEntity
from src.app.infrastructure.database.models.product_model import Product


class CreateProductUseCase:
    def __init__(
        self,
        product_repository: ProductRepositoryInterface,
        price_history_repository: PriceHistoryRepositoryInterface,
    ):
        self.product_repository = product_repository
        self.price_history_repository = price_history_repository

    def execute(self, product: ProductEntity, initial_price: float):
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

    def execute(
        self,
        filter_data: Dict[str, Any],
        limit: int,
        offset: int,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> tuple[List[Product], int]:
        column_filters = filter_data.get("column_filters", {})

        return self.product_repository.get_all(
            column_filters=column_filters,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )


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

            retrieved_product = self.product_repository.get_by_id(updated_product.id)
            return retrieved_product
        return updated_product


class DeleteProductUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, product_id: int) -> bool:
        return self.product_repository.delete(product_id)


class SearchProductsUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, query: str, limit: int, offset: int) -> List[ProductEntity]:
        return self.product_repository.search_products(
            query=query, limit=limit, offset=offset
        )


class FilterProductsUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(
        self, filter_data: Dict, limit: int, offset: int
    ) -> List[ProductEntity]:
        return self.product_repository.filter_products(
            filter_data=filter_data, limit=limit, offset=offset
        )


class GetProductStatsUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self) -> dict:
        return self.product_repository.get_product_stats()


class GetMinimalProductsUseCase:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def execute(self, limit: int, offset: int) -> List[dict]:
        return self.product_repository.get_minimal_products(limit=limit, offset=offset)
