import cloudscraper

from requests import Response
from cloudscraper import requests

from product_scrapers.scrapers.interfaces import Scraper


class EnjoeiScraper(Scraper):
    def __init__(self):
        self.BASE_URL = "https://enjusearch.enjoei.com.br"
        self.session = cloudscraper.create_scraper()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "DNT": "1",
            "Sec-GPC": "1",
        }
        self.session.headers.update(self.headers)

    def _make_request(self, url: str) -> object:
        try:
            response = self.session.get(url, allow_redirects=True)
            response.raise_for_status()
            return response.text

        except requests.exceptions.HTTPError as e:
            status_code = getattr(e.response, "status_code", "unknown")
            print(f"HTTP error {status_code} em {url}")

        except requests.exceptions.RequestException as e:
            print(f"Connection error: {str(e)}")

        except Exception as e:
            print(f"Unexpected error: {str(e)}")

        return None

    def _get_search_data(self, term: str, after: str = None) -> Response:
        params = {
            "first": "50",  # seens like 50 is the maximum
            "query_id": "7d3ea67171219db36dfcf404acab5807",
            "search_id": "88d3a54e-085a-46bc-a1f8-9726ee34424a-1743974498480",
            "term": term,
        }

        if after:
            params["after"] = after

        return self.session.get(
            f"{self.BASE_URL}/graphql-search-x",
            headers=self.headers,
            params=params,
        )

    def _extract_links(self, data: dict) -> tuple:
        urls = []
        cursor = None
        result_pages_url = "https://pages.enjoei.com.br/products"

        try:
            edges = (
                data.get("data", {})
                .get("search", {})
                .get("products", {})
                .get("edges", [])
            )
            for edge in edges:
                node = edge["node"]
                if "id" in node:
                    product_id = node["id"]
                    urls.append(f"{result_pages_url}/{product_id}/v2.json")

                    if "cursor" in edge:
                        cursor = edge["cursor"]

        except (KeyError, TypeError, AttributeError):
            pass

        return urls, cursor

    def search(self, search_term: str) -> list[str]:
        all_urls = []
        cursor = None
        while True:
            response = self._get_search_data(term=search_term, after=cursor)
            urls, cursor = self._extract_links(response.json())
            all_urls.extend(urls)
            if not cursor:
                break
        return all_urls

    def scrape_data(self, url: str) -> dict:
        response = self.session.get(url)
        data = response.json()
        url = data["canonical_url"]
        price_dict = data.get("fallback_pricing", {}).get("price", {})
        price = price_dict.get("listed") or price_dict.get("sale") or "0"

        return {
            "url": url,
            "title": data.get("title"),
            "price": price,
        }

    def update_data(self, product: dict) -> dict:
        product_code = product["url"].split("-")[-1]
        api_url = f"https://pages.enjoei.com.br/products/{product_code}/v2.json"
        updated_data = self.scrape_data(api_url)
        return {**product, **updated_data}

    def __str__(self):
        return "Enjoei Scraper"
