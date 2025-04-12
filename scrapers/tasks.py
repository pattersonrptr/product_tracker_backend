import os
from datetime import datetime, timedelta

import requests

from celery import Celery, group, chord
from celery.schedules import crontab

from scrapers.base.scraper import Scraper
from scrapers.enjoei.scraper import EnjoeiScraper
from scrapers.olx.scraper import OLXScraper

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
app = Celery(main="scrapers", broker=broker_url, backend="redis://redis:6379/0")

SEARCHES = ["livros python"]


def get_scraper(scraper_name: str) -> Scraper:
    if scraper_name == "olx":
        return OLXScraper()
    elif scraper_name == "enjoei":
        return EnjoeiScraper()
    else:
        raise ValueError(f"Unknown scraper: {scraper_name}")


@app.task(name="scrapers.tasks.run_scraper_searches")
def run_scraper_searches(scraper_name: str = "olx"):
    return group(run_search.s(search, scraper_name) for search in SEARCHES)()


@app.task(name="scrapers.tasks.run_search")
def run_search(search: str, scraper_name: str):
    print(f"🔎 Searching term: {search} with {scraper_name}")
    scraper = get_scraper(scraper_name)

    try:
        api_url = f"{os.getenv('API_URL', 'http://web:8000')}/products/"
        response = requests.get(api_url)

        existing_products = response.json() if response.status_code == 200 else []
        existing_urls = {
            p["url"] for p in existing_products if scraper_name in p["url"]
        }

        urls = scraper.search(search)
        new_urls = list(set(urls) - existing_urls)

        print(f"New: {len(new_urls)}")
        print(f"Existing: {len(existing_urls)}")
        print(f"Found {len(urls)} URLs, {len(new_urls)} are new")

        process_url_list.apply_async(
            args=[
                {"status": "success", "search": search, "urls": new_urls},
                scraper_name,
            ],
            countdown=10,
        )
        return {"status": "success", "search": search, "urls": new_urls}
    except Exception as e:
        return {"status": "error", "search": search, "message": str(e)}


@app.task(name="scrapers.tasks.process_url_list")
def process_url_list(result, scraper_name: str):
    print(f"📥 Processing {len(result['urls'])} URLs of {result['search']}")

    return chord(
        scrape_product_page.s(url, scraper_name).set(countdown=10)
        for url in result["urls"]
    )(save_products.s())


@app.task(name="scrapers.tasks.scrape_product_page")
def scrape_product_page(url: str, scraper_name: str):
    print(f"🛒 Get products data for{url} with {scraper_name}")
    scraper = get_scraper(scraper_name)

    try:
        product_data = scraper.scrape_data(url)
        return {"status": "success", "data": product_data}
    except Exception as e:
        return {"status": "error", "url": url, "message": str(e)}


@app.task(name="scrapers.tasks.save_products")
def save_products(results):
    successful = [r["data"] for r in results if r["status"] == "success"]
    print(f"💾 Saving {len(successful)} products")

    print("Successful: ", successful)
    print("Successful[0]: ", successful[0])

    api_url = f"{os.getenv('API_URL', 'web:8000')}/products/"
    created = 0

    for product in successful:
        response = requests.get(api_url, params={"url": product["url"]})
        if response.status_code == 200 and response.json():
            continue

        response = requests.post(api_url, json=product, timeout=10)
        if response.status_code == 201:
            created += 1

    return f"✅ {created} new products created"


@app.task(name="scrapers.tasks.run_scraper_update")
def run_scraper_update(scraper_name: str):
    print("Updating products by URLs")

    cutoff_date = (datetime.today() - timedelta(days=30)).date()
    api_url = f"{os.getenv('API_URL', 'http://web:8000')}/products/?updated_before={cutoff_date}"
    response = requests.get(api_url)
    products = []

    if response.status_code == 200 and response.json():
        products = response.json()

    return chord(
        update_product.s(product, scraper_name).set(countdown=10)
        for product in products
    )(update_products.s())


@app.task(name="scrapers.tasks.update_product")
def update_product(product: dict, scraper_name: str):
    print(f"🛒 Scraping URL: {product['url']}")

    scraper = get_scraper(scraper_name)

    try:
        product_data = scraper.update_data(product)
        return {"status": "success", "data": product_data}
    except Exception as e:
        return {"status": "error", "url": product["url"], "message": str(e)}


@app.task(name="scrapers.tasks.update_products")
def update_products(results):
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
    "run_olx_searches_daily": {
        "task": "scrapers.tasks.run_scraper_searches",
        "schedule": crontab(hour="00", minute="00"),
        "args": ("olx",),
    },
    "run_enjoei_searches_daily": {
        "task": "scrapers.tasks.run_scraper_searches",
        "schedule": crontab(hour="01", minute="00"),
        "args": ("enjoei",),
    },
    "run_olx_scraper_update_daily": {
        "task": "scrapers.tasks.run_scraper_update",
        "schedule": crontab(hour="02", minute="00"),
        "args": ("olx",),
    },
    "run_enjoei_scraper_update_daily": {
        "task": "scrapers.tasks.run_scraper_update",
        "schedule": crontab(hour="03", minute="00"),
        "args": ("enjoei",),
    },
}

app.conf.timezone = "America/Sao_Paulo"
