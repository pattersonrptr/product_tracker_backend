import json
import cloudscraper

from bs4 import BeautifulSoup

from product_scrapers.scrapers.interfaces.scraper_interface import ScraperInterface


class EstanteVirtualScraper(ScraperInterface):
    def __init__(self):
        self.BASE_URL = "https://www.estantevirtual.com.br"

        self.session = cloudscraper.create_scraper()
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
        }
        self.session.headers.update(self.headers)

    def search(self, search_term: str) -> list[str]:
        page_number = 0
        has_next = True
        all_links = []

        while has_next:
            page_number += 1

            params = {
                "q": search_term,
                "searchField": "titulo-autor",
                "page": f"{page_number}",
            }

            resp = self.session.get(
                f"{self.BASE_URL}/busca/api",
                params=params,
                headers=self.headers,
            )

            if page_number == resp.json().get("totalPages"):
                has_next = False
            else:
                urls = self._get_products_list(resp.json())
                all_links.extend(urls)

        return all_links

    def _get_products_list(self, data: dict) -> list:
        return [f"{self.BASE_URL}{item['productSlug']}" for item in data["parentSkus"]]

    def scrape_data(self, url: str) -> dict:
        resp = self._fetch_page(url)
        soup = self._parse_html(resp.content)
        data = self._extract_initial_state(soup)
        if not data:
            return {}

        product_info = self._extract_product_info(data)
        prices = self._extract_prices(product_info)
        price = self._get_lowest_price(prices)
        description = self._extract_description(product_info)
        seller, location = self._extract_seller_and_location(product_info)

        return {
            "url": url,
            "product_name": f"{product_info.get('name', '')} | {product_info.get('author', '')}",
            "price": f"R$ {price:.2f}" if price else "",
            "description": description,
            "seller": seller,
            "location": location,
        }

    def _fetch_page(self, url: str):
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp

    def _parse_html(self, content: bytes) -> BeautifulSoup:
        return BeautifulSoup(content, "html.parser")

    def _extract_initial_state(self, soup: BeautifulSoup) -> dict:
        script_tag = soup.find(
            "script", string=lambda t: t and "window.__INITIAL_STATE__" in t
        )
        if not script_tag:
            return {}
        json_data = script_tag.string.split("=", 1)[1].strip().rstrip(";")
        return json.loads(json_data)

    def _extract_product_info(self, data: dict) -> dict:
        return data.get("Product", {})

    def _extract_prices(self, product_info: dict) -> list:
        grouper = product_info.get("grouper", {})
        group_products = grouper.get("groupProducts", {})
        prices = []
        for condition in ["novo", "usado"]:
            if condition in group_products:
                price = (
                    group_products[condition].get("salePrice", 0) / 100
                )  # Convert from cents
                prices.append(price)
        return prices

    def _get_lowest_price(self, prices: list) -> float:
        return min(prices) if prices else 0

    def _extract_description(self, product_info: dict) -> str:
        return product_info.get("currentProduct", {}).get("description", "")

    def _extract_seller_and_location(self, product_info: dict) -> tuple:
        grouper = product_info.get("grouper", {})
        group_products = grouper.get("groupProducts", {})
        for condition in ["novo", "usado"]:
            if condition in group_products:
                prices_list = group_products[condition].get("prices", [])
                if prices_list:
                    seller = prices_list[0].get("sellerName", "")
                    location = prices_list[0].get("city", "")
                    return seller, location
        return "", ""

    def update_data(self, product: dict) -> dict:
        data = self.scrape_data(product["url"])
        return {**product, **data}

    def __str__(self):
        return "Estante Virtual Scraper"
