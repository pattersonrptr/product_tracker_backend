from abc import ABC, abstractmethod
from typing import List, Optional

from app.entities.product.product import Product


class ProductRepositoryInterface(ABC):
    @abstractmethod
    def create(self, product: Product) -> Product:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        raise NotImplementedError

    @abstractmethod
    def get_by_url(self, url: str) -> Optional[Product]:
        raise NotImplementedError

    @abstractmethod
    def get_all(self, limit: int, offset: int) -> List[Product]:
        raise NotImplementedError

    @abstractmethod
    def update(self, product_id: int, product: Product) -> Optional[Product]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def search_products(self, query: str, limit: int, offset: int) -> List[Product]:
        raise NotImplementedError

    @abstractmethod
    def filter_products(self, filter_data: dict) -> List[Product]:
        raise NotImplementedError

    @abstractmethod
    def get_product_stats(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_minimal_products(self) -> List[dict]:
        raise NotImplementedError
