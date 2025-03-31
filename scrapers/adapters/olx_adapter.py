from scrapers.olx.scraper import Scraper
from .base import BaseScraperAdapter

class OLXAdapter(BaseScraperAdapter):
    def __init__(self):
        self.scraper = Scraper()

    def search_products(self, search_term: str) -> list[str]:
        return self.scraper.scrape_search(search_term)

    def scrape_product(self, url: str) -> dict:
        return self.scraper.scrape_product_page(url)

    def update_product(self, product: dict) -> dict:
        return self.scraper.update_product(product)
