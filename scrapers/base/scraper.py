from abc import ABC, abstractmethod


class Scraper(ABC):
    @abstractmethod
    def search(self, search_term: str) -> list[str]:
        """Return a list of product URLs for a search term."""
        pass

    @abstractmethod
    def scrape_data(self, url: str) -> dict:
        """Return normalized product data from a product page URL."""
        pass

    @abstractmethod
    def update_data(self, product: dict) -> dict:
        """Update an existing product's data."""
        pass
