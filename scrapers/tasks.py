import os
import requests

from celery import Celery, group, chord
from celery.schedules import crontab

from scrapers.adapters.olx_adapter import OLXAdapter
from scrapers.adapters.enjoei_adapter import EnjoeiAdapter

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
app = Celery(main="scrapers", broker=broker_url, backend="redis://redis:6379/0")

SEARCHES = ["livros python"]


def get_scraper_adapter(scraper_name: str):
    if scraper_name == "olx":
        return OLXAdapter()
    elif scraper_name == "enjoei":
        return EnjoeiAdapter()
    else:
        raise ValueError(f"Unknown scraper: {scraper_name}")

@app.task(name="scrapers.tasks.run_scraper_searches")
def run_scraper_searches(scraper_name: str = "olx"):
    return group(
        run_search.s(search, scraper_name) for search in SEARCHES
    )()

@app.task(name="scrapers.tasks.run_search")
def run_search(search: str, scraper_name: str):
    print(f"🔎 Searching term: {search} with {scraper_name}")
    adapter = get_scraper_adapter(scraper_name)

    try:
        urls = adapter.search_products(search)
        api_url = f"{os.getenv('API_URL', 'http://web:8000')}/products/"
        response = requests.get(api_url)
        existing_products = response.json() if response.status_code == 200 else []
        existing_urls = {p["url"] for p in existing_products}
        new_urls = list(set(urls) - existing_urls)

        print(f"New: {len(new_urls)}")
        print(f"Existing: {len(existing_urls)}")
        print(f"Found {len(urls)} URLs, {len(new_urls)} are new")

        process_url_list.apply_async(
            args=[{"status": "success", "search": search, "urls": new_urls}, scraper_name],
            countdown=10,
        )
        return {"status": "success", "search": search, "urls": new_urls}
    except Exception as e:
        return {"status": "error", "search": search, "message": str(e)}


@app.task(name="scrapers.tasks.process_url_list")
def process_url_list(result, scraper_name: str):
    print(f"📥 Processing {len(result['urls'])} URLs of {result['search']}")

    return chord(
        scrape_product_page.s(url, scraper_name).set(countdown=10) for url in result["urls"]
    )(save_products.s())

@app.task(name="scrapers.tasks.scrape_product_page")
def scrape_product_page(url: str, scraper_name: str):
    print(f"🛒 Get products data for{url} with {scraper_name}")
    adapter = get_scraper_adapter(scraper_name)

    try:
        product_data = adapter.scrape_product(url)
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

# TODO: Implement update and test tasks.
# TODO: Too much logic in the tasks, maybe moving too a separated file could be be better, and helps unit testing.
# TODO: Unit test these tasks.
# TODO: Call Celery beat update tasks.


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
    # "run_olx_scraper_update_daily": {
    #     "task": "scrapers.tasks.run_olx_scraper_update",
    #     "schedule": crontab(hour="02", minute="00"),
    # },
}

app.conf.timezone = "America/Sao_Paulo"
