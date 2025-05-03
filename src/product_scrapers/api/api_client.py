# TODO: Use logging instead of simple prints. It's better to decouple the logging logic, maybe having a logger class.

import os
from typing import List, Dict, Any

import requests


class ApiClient:
    def __init__(self, access_token=None):
        self.base_url = os.getenv("API_URL", "web:8000")
        self.access_token = access_token
        self.headers = {}

        if self.access_token:
            self.headers["Authorization"] = f"Bearer {self.access_token}"

    def _make_request(
        self, method: str, endpoint: str, data: dict = None, params: dict = None
    ) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method, url, headers=self.headers, json=data, params=params, timeout=10
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"🔴 Request error at {url}: {e}")
            return requests.Response()

    def get_active_searches(self) -> List[Dict[str, Any]]:
        # TODO: This is temporarily, it is better to have get_active_searches endpoint in the API.
        print("🔎 Getting search configs")
        response = self._make_request("GET", "/search_configs/")
        return (
            [item for item in response.json() if item.get("is_active")]
            if response.status_code == 200
            else []
        )

    def get_source_website_by_name(self, website_name: str) -> Dict[str, Any]:
        print(f"🔎 Checking if source website {website_name} exists")
        response = self._make_request("GET", f"/source_websites/name/{website_name}")
        return (
            response.json() if response.status_code == 200 and response.json() else {}
        )

    def get_existing_product_urls(self, scraper_name):
        print("🔎 Checking existing products")
        response = self._make_request("GET", "/products/")
        existing_products = response.json() if response.status_code == 200 else []
        return {p["url"] for p in existing_products if scraper_name in p["url"]}

    def create_product(self, product):
        print(f"💾 Creating product: {product['url']}")
        response = self._make_request("POST", "/products/", data=product)
        return response.status_code == 201

    def product_exists(self, product) -> bool:
        print("🔎 Checking if product exists")
        response = self._make_request("GET", f"/products/url/{product["url"]}")
        if response.status_code == 200 and response.json():
            print(response.status_code)
            print(response.json())
            return True
        return False

    def create_new_products(self, products: list[dict]) -> int:
        print(f"💾 Saving {len(products)} products")
        created = 0
        for product in products:
            if not self.product_exists(product):
                if self.create_product(product):
                    created += 1
        print(f"✅ {created} new products created")
        return created

    def get_products(self, params=None):
        print("🔄 Updating products by URLs")
        response = self._make_request("GET", "/products/filter/", params=params)
        return (
            response.json() if response.status_code == 200 and response.json() else []
        )

    def update_product_list(self, products):
        print(f"💾 Updating {len(products)} products")
        updated = 0
        for product in products:
            print(80 * "-")
            print(product)
            print(80 * "-")
            response = self._make_request(
                "PUT", f"/products/{product['id']}", data=product
            )
            if response.status_code == 200:
                updated += 1
        print(f"✅ {updated} products updated")
        return updated
