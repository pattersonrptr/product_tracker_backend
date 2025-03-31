from abc import ABC, abstractmethod

class BaseScraperAdapter(ABC):
    @abstractmethod
    def search_products(self, search_term: str) -> list[str]:
        """Return a list of product URLs for a search term."""
        pass

    @abstractmethod
    def scrape_product(self, url: str) -> dict:
        """Return normalized product data from a product page URL."""
        pass

    @abstractmethod
    def update_product(self, product: dict) -> dict:
        """Update an existing product's data."""
        pass
