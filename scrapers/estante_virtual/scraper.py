import cloudscraper
import json
from bs4 import BeautifulSoup

from scrapers.base.scraper import Scraper


class EstanteVirtualScraper(Scraper):
    def __init__(self):
        self.BASE_URL = "https://www.estantevirtual.com.br"

        self.session = cloudscraper.create_scraper()
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
        }
        self.session.headers.update(self.headers)

    def search(self, search_term: str) -> list[str]:
        params = {
            "q": search_term,
            "searchField": "titulo-autor",
        }

        return self.session.get(
            f"{self.BASE_URL}/busca/api",
            params=params,
            headers=self.headers,
        )

    def _get_products_list(self, data: dict) -> list:
        return [
            {
                "url": f"{self.BASE_URL}{item['productSlug']}",
                "title": item.get("name"),
                "price": str(item.get("salePrice") / 100).replace(".", ","),
            }
            for item in data["parentSkus"]
        ]

    def scrape_data(self, url: str) -> dict:
        resp = self.session.get(url)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.content, "html.parser")

        # Find the script tag containing __INITIAL_STATE__
        script_tag = soup.find(
            "script", string=lambda t: t and "window.__INITIAL_STATE__" in t
        )
        if not script_tag:
            return {}

        # Extract JSON data from the script
        json_data = script_tag.string.split("=", 1)[1].strip().rstrip(";")
        data = json.loads(json_data)

        # Extract product information from JSON
        product_info = data.get("Product", {})
        grouper = product_info.get("grouper", {})
        group_products = grouper.get("groupProducts", {})

        # Get product name and author
        product_name = product_info.get("name", "")
        author = product_info.get("author", "") or product_info.get(
            "formattedAttributes", {}
        ).get("author", "")

        # Get prices (new and used)
        prices = []
        for condition in ["novo", "usado"]:
            if condition in group_products:
                price = (
                    group_products[condition].get("salePrice", 0) / 100
                )  # Convert from cents
                prices.append(price)

        # Get lowest price available
        price = min(prices) if prices else ""

        # Get description
        description = product_info.get("currentProduct", {}).get("description", "")

        # Get seller and location from the first available product variant
        seller = ""
        location = ""
        for condition in ["novo", "usado"]:
            if condition in group_products:
                prices_list = group_products[condition].get("prices", [])
                if prices_list:
                    seller = prices_list[0].get("sellerName", "")
                    location = prices_list[0].get("city", "")
                    break

        return {
            "url": url,
            "product_name": f"{product_name} | {author}",
            "price": f"R$ {price:.2f}" if price else "",
            "description": description,
            "seller": seller,
            "location": location,
        }

    def update_data(self, product: dict) -> dict:
        data = self.scrape_data(product["url"])
        return {**product, **data}
