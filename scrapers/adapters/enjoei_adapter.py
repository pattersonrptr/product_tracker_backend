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
        price_dict = data.get('fallback_pricing', {}).get('price', {})

        # TODO: When trying to save with price 0 got an error '422 Unprocessable entity', probably because the schema
        #  expect a number not None. Need to handle this in the save() task not here.
        #  Then here I should stop assigning 0
        price = price_dict.get('listed') or price_dict.get('sale') or '0'

        return {
            "url": url,    #TODO: Returning Enjoei API product URL, but need to return the URL that appears in browser
            "title": data.get("title"),
            "price": price,
        }

    def update_product(self, product: dict) -> dict:
        updated_data = self.scrape_product(product["url"])
        return {**product, **updated_data}