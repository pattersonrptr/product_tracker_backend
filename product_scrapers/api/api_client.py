# TODO: Use logging instead of simple prints.
# TODO: Better decouple the logging logic, maybe having a logger class.

import os
from typing import List, Dict, Any

import requests


class ApiClient:
    def __init__(self):
        self.base_url = os.getenv("API_URL", "web:8000")

    def get_active_searches(self) -> List[Dict[str, Any]]:
        # TODO: This is temporarily, it is better to have get_active_searches endpoint in the API.
        print("🔎 Getting search configs")
        api_url = f"{self.base_url}/search_configs/"
        response = requests.get(api_url)

        if response.status_code != 200:
            return []

        return [item for item in response.json() if item.get("is_active")]

    def get_source_website_by_name(self, website_name: str) -> Dict[str, Any]:
        print(f"🔎 Checking if source website {website_name} exists")
        api_url = f"{self.base_url}/source_websites/name/{website_name}"
        response = requests.get(api_url)

        if response.status_code == 200 and response.json():
            return response.json()
        return {}

    def get_existing_product_urls(self, scraper_name):
        print("🔎 Checking existing products")
        api_url = f"{self.base_url}/products/"
        response = requests.get(api_url)
        existing_products = response.json() if response.status_code == 200 else []

        existing_urls = {
            p["url"] for p in existing_products if scraper_name in p["url"]
        }
        return existing_urls

    def create_product(self, product):
        print(f"💾 Creating product: {product['url']}")

        print(">>>>>>>>>> DEBUG api.client.create_product >>>>>>>>>>")
        print(product)
        print(">>>>>>>>>> DEBUG api.client.create_product >>>>>>>>>>")

        api_url = f"{self.base_url}/products/"
        resp = requests.post(api_url, json=product, timeout=10)

        if resp.status_code == 201:
            return True
        return False

    def product_exists(self, product) -> bool:
        print("🔎 Checking if product exists")

        api_url = f"{self.base_url}/products/url/{product["url"]}"
        resp = requests.get(api_url)

        if resp.status_code == 200 and resp.json():
            print(resp.status_code)
            print(resp.json())
            return True
        return False

    def create_new_products(self, products: list[dict]) -> int:
        print(f"💾 Saving {len(products)} products")
        created = 0

        for product in products:
            if self.product_exists(product):
                print(f"🔴 Product already exists: {product['url']}")
                continue

            if self.create_product(product):
                created += 1

        print(f"✅ {created} new products created")

        return created

    def get_products(self, params=None):
        print("🔄 Updating products by URLs")

        api_url = f"{self.base_url}/products/filter/"
        resp = requests.get(api_url, params=params)

        if resp.status_code == 200 and resp.json():
            return resp.json()

        return []

    def update_product_list(self, products):
        print(f"💾 Updating {len(products)} products")
        updated = 0

        for product in products:
            print(80 * "-")
            print(product)
            print(80 * "-")

            api_url = f"{self.base_url}/products/{product['id']}"
            response = requests.put(api_url, json=product, timeout=10)

            if response.status_code == 200:
                updated += 1

        print(f"✅ {updated} products updated")

        return updated
