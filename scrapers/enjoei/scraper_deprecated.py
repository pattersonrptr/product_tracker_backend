import os
import cloudscraper

from requests import Response

# TODO: Maybe could be useful to add the method safe_request()


class Scraper:
    def __init__(self, api_url=None):
        self.BASE_URL = "https://enjusearch.enjoei.com.br"
        self.session = cloudscraper.create_scraper()
        env_api_url = os.getenv("API_URL", "")
        self.api_url = api_url or (env_api_url if env_api_url else "web:8000")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "DNT": "1",
            "Sec-GPC": "1",
        }
        self.timeouts = (5, 15)  # (connect, read)
        self.session.headers.update(self.headers)

    def search(self, term: str, after: str = None) -> Response:
        params = {
            "browser_id": "07176e90-ef8c-4a5a-976b-b68d3a42fdeb-1742160795598",
            "city": "atibaia",
            "first": "30",
            "new_buyer": "false",
            "operation_name": "searchProducts",
            "query_id": "7d3ea67171219db36dfcf404acab5807",
            "search_context": "products_search",
            "search_id": "d89a6bf8-7b44-4e94-a4ff-2dd8e70930f4-1743294487254",
            "shipping_range": "near_regions",
            "state": "sp",
            "term": term,
            "user_id": "34906900",
        }

        if after:
            params["after"] = after

        return self.session.get(
            f"{self.BASE_URL}/graphql-search-x",
            headers=self.headers,
            params=params,
        )

    def extract_links(self, data: dict) -> tuple:
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

    def get_product_data(self, url: str) -> Response:
        return self.session.get(url, headers=self.headers)
