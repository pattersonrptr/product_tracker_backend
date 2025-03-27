from datetime import datetime, timedelta

from celery import Celery, group, chord
from celery.schedules import crontab
from scrapers.olx.scraper import Scraper
import os
import time
import random
import requests

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")

app = Celery(
    main='scrapers',
    broker=broker_url,
    backend='redis://redis:6379/0'
)

# app.conf.update(
#     task_concurrency=16,
#     worker_prefetch_multiplier=10,
#     worker_heartbeat=120,
# )

SEARCHES = ["livro python"]


@app.task(name="scrapers.tasks.run_olx_scraper_searches")
def run_olx_scraper_searches():
    """Task 1: Trigger a task for each search term"""
    return group(run_olx_scraper.s(search) for search in SEARCHES)()


@app.task(name="scrapers.tasks.run_olx_scraper")
def run_olx_scraper(search):
    """Task 2: Run the scraper for a search term and return URLs"""
    print(f"🔎 Searching term: {search}")

    scraper = Scraper()
    try:
        urls = scraper.scrape_search(search)

        api_url = f"{os.getenv('API_URL', 'http://web:8000')}/products/"
        response = requests.get(api_url)


        existing_products = response.json() if response.status_code == 200 else []
        existing_urls = {p['url'] for p in existing_products}

        new_urls = list(set(urls) - existing_urls)

        print(f"New: {len(new_urls)}")
        print(f"Existing: {len(existing_urls)}")

        print(f"Found {len(urls)} URLs, {len(new_urls)} are new")


        # Call Task 3 ASYNCHRONOUSLY with the results
        process_url_list.apply_async(
            args=[{"status": "success", "search": search, "urls": new_urls}],
            countdown=10
        )
        return {"status": "success", "search": search, "urls": new_urls}
    except Exception as e:
        return {"status": "error", "search": search, "message": str(e)}


@app.task(name="scrapers.tasks.process_url_list")
def process_url_list(result):
    """Task 3: Processes URLs and coordinates Tasks 4 and 5"""
    print(f"📥 Processing {len(result['urls'])} URLs of {result['search']}")

    # Create a chord with Tasks 4 and trigger Task 5 at the end
    return chord(
        scrape_product_page.s(url).set(countdown=10) for url in result["urls"]
    )(save_products.s())


@app.task(name="scrapers.tasks.scrape_product_page")
def scrape_product_page(url):
    """Task 4: Collect product data from URL"""
    print(f"🛒 Scraping URL: {url}")

    scraper = Scraper()

    try:
        product_data = scraper.scrape_product_page(url)
        return {"status": "success", "data": product_data}
    except Exception as e:
        return {"status": "error", "url": url, "message": str(e)}


@app.task(name="scrapers.tasks.save_products")
def save_products(results):
    """Task 5: Save products to the database via API"""
    successful = [r["data"] for r in results if r["status"] == "success"]
    print(f"💾 Saving {len(successful)} products")

    api_url = f"{os.getenv('API_URL', 'web:8000')}/products/"
    created = 0

    for product in successful:
        # Check if product already exists
        response = requests.get(api_url, params={"url": product["url"]})
        if response.status_code == 200 and response.json():
            continue

        response = requests.post(api_url, json=product, timeout=10)
        if response.status_code == 201:
            created += 1

    return f"✅ {created} new products created"


@app.task(name="scrapers.tasks.run_olx_scraper_update")
def run_olx_scraper_update():
    print("Updating products by URLs")

    cutoff_date = (datetime.today() - timedelta(days=30)).date()
    api_url = f"{os.getenv('API_URL', 'web:8000')}/products/?updated_before={cutoff_date}"
    response = requests.get(api_url)
    products = []

    if response.status_code == 200 and response.json():
        products = response.json()

    return chord(
        update_product.s(product).set(countdown=10) for product in products
    )(update_products.s())


@app.task(name="scrapers.tasks.update_product")
def update_product(product):
    print(f"🛒 Scraping URL: {product['url']}")

    scraper = Scraper()

    try:
        product_data = scraper.update_product(product)
        return {"status": "success", "data": product_data}
    except Exception as e:
        return {"status": "error", "url": product['url'], "message": str(e)}


@app.task(name="scrapers.tasks.update_products")
def update_products(results):
    """Update products in the database via API"""
    successful = [r["data"] for r in results if r["status"] == "success"]
    print(f"💾 Updating {len(successful)} products")

    updated = 0

    for product in successful:
        api_url = f"{os.getenv('API_URL', 'web:8000')}/products/{product['id']}"
        response = requests.put(api_url, json=product, timeout=10)

        if response.status_code == 200:
            updated += 1

    return f"✅ {updated} products updated"


app.conf.beat_schedule = {
    'run_olx_scraper_searches_daily': {
        'task': 'scrapers.tasks.run_olx_scraper_searches',
        'schedule': crontab(hour="00", minute="00"),
    },
    'run_olx_scraper_update_daily': {
        'task': 'scrapers.tasks.run_olx_scraper_update',
        'schedule': crontab(hour="02", minute="00"),
    },
}

app.conf.timezone = 'America/Sao_Paulo'