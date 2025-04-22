import os
import requests


class ProductApiClient:
    def __init__(self):
        self.base_url = os.getenv("API_URL", "web:8000")

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
        api_url = f"{self.base_url}/products/"
        resp = requests.post(api_url, json=product, timeout=10)
        if resp.status_code == 201:
            return True
        return False

    def product_exists(self, product) -> bool:
        print("🔎 Checking if product exists")

        api_url = f"{self.base_url}/products/"
        resp = requests.get(api_url, params={"url": product["url"]})
        if resp.status_code == 200 and resp.json():
            return True
        return False

    def create_new_products(self, products: list[dict]) -> int:
        print(f"💾 Saving {len(products)} products")
        created = 0

        for product in products:
            if self.product_exists(product):
                print(f"🔴 Product already exists: {product['url']}")
                continue

            created += 1
            self.create_product(product)

        print(f"✅ {created} new products created")

        return created

    def get_products(self, params=None):
        print("🔄 Updating products by URLs")

        api_url = f"{self.base_url}/products/"
        resp = requests.get(api_url, params=params)

        if resp.status_code == 200 and resp.json():
            return resp.json()

        return []

    def update_product_list(self, products):
        print(f"💾 Updating {len(products)} products")
        updated = 0
        for product in products:
            api_url = f"{self.base_url}/products/{product['id']}"
            response = requests.put(api_url, json=product, timeout=10)

            if response.status_code == 200:
                updated += 1

        print(f"✅ {updated} products updated")

        return updated
