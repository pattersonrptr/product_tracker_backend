from scrapers.enjoei.scraper import Scraper
from .base import BaseScraperAdapter

class EnjoeiAdapter(BaseScraperAdapter):
    def __init__(self):
        self.scraper = Scraper()

    def search_products(self, search_term: str) -> list[str]:
        all_urls = []
        cursor = None
        while True:
            response = self.scraper.search(term=search_term, after=cursor)
            urls, cursor = self.scraper.extract_links(response.json())
            all_urls.extend(urls)
            if not cursor:
                break
        return all_urls

    def scrape_product(self, url: str) -> dict:
        response = self.scraper.get_product_data(url)
        data = response.json()
        return {
            "url": url,
            "title": data.get("title"),
            "price": data.get("price"),
        }

    def update_product(self, product: dict) -> dict:
        updated_data = self.scrape_product(product["url"])
        return {**product, **updated_data}
