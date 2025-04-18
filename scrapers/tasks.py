import os
from datetime import datetime, timedelta

from celery import Celery, group, chord
from celery.schedules import crontab

from app.models import SearchConfig
from app.database import SessionLocal
from scrapers.product_api_client import ProductApiClient
from scrapers.scraper_manager import ScraperManager

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
app = Celery(main="scrapers", broker=broker_url, backend="redis://redis:6379/0")


def get_active_searches():
    db = SessionLocal()
    try:
        return [
            search.search_term
            for search in db.query(SearchConfig).filter(SearchConfig.is_active).all()
        ]
    finally:
        db.close()


@app.task(name="scrapers.tasks.run_scraper_searches")
def run_scraper_searches(scraper_name: str = "olx"):
    active_searches = get_active_searches()
    return group(run_search.s(search, scraper_name) for search in active_searches)()


@app.task(name="scrapers.tasks.run_search")
def run_search(search: str, scraper_name: str):
    api_cli = ProductApiClient()
    scraper = ScraperManager(scraper_name)
    existing_urls = api_cli.get_existing_product_urls(scraper_name)
    urls = scraper.get_products_urls(search)
    new_urls = scraper.get_urls_to_update(existing_urls, urls)

    process_urls_list.apply_async(
        args=[
            {"status": "success", "search": search, "urls": new_urls},
            scraper_name,
        ],
        countdown=10,
    )
    return {"status": "success", "search": search, "urls": new_urls}


@app.task(name="scrapers.tasks.process_urls_list")
def process_urls_list(search_results: dict, scraper_name: str):
    scraper = ScraperManager(scraper_name)
    chunks = scraper.split_search_urls(search_results, 100)

    task_group = group(
        chord(
            scrape_product_page.s(url, scraper_name).set(countdown=5) for url in chunk
        )(save_products.s())
        for chunk in chunks
    )

    return task_group.apply_async()


@app.task(name="scrapers.tasks.scrape_product_page")
def scrape_product_page(url: str, scraper_name: str):
    scraper = ScraperManager(scraper_name)

    try:
        product_data = scraper.scrape_product(url)
        return {"status": "success", "data": product_data}
    except Exception as e:
        return {"status": "error", "url": url, "message": str(e)}


@app.task(name="scrapers.tasks.save_products")
def save_products(results):
    # TODO: Next improvement cold be to save the products in batches

    successful = [r["data"] for r in results if r["status"] == "success"]
    api_client = ProductApiClient()
    created = api_client.create_new_products(successful)

    return {"status": "success", "created": created}


@app.task(name="scrapers.tasks.run_scraper_update")
def run_scraper_update(scraper_name: str):
    api_cli = ProductApiClient()
    cutoff_date = (datetime.today() - timedelta(days=30)).date()
    products = api_cli.get_products({"updated_before": cutoff_date})

    return chord(
        update_product.s(product, scraper_name).set(countdown=10)
        for product in products
    )(update_products.s())


@app.task(name="scrapers.tasks.update_product")
def update_product(product: dict, scraper_name: str):
    scraper = ScraperManager(scraper_name)

    try:
        product_data = scraper.update_product(product)
        return {"status": "success", "data": product_data}
    except Exception as e:
        return {"status": "error", "url": product["url"], "message": str(e)}


@app.task(name="scrapers.tasks.update_products")
def update_products(results):
    api_cli = ProductApiClient()
    successful = [r["data"] for r in results if r["status"] == "success"]
    updated = api_cli.update_product_list(successful)

    return {"status": "success", "updated_count": updated}


# TODO: Uncomment this function to enable dynamic scheduling - Obs: needs somes fixes
# def get_dynamic_schedule():
#     from app.database import SessionLocal
#     db = SessionLocal()
#     try:
#         schedules = {}
#         searches = db.query(SearchConfig).filter(SearchConfig.is_active == True).all()
#
#         for idx, search in enumerate(searches):
#             schedules[f"run_search_{search.id}"] = {
#                 "task": "scrapers.tasks.run_scraper_searches",
#                 "schedule": crontab(
#                     hour=search.preferred_time.hour,
#                     minute=search.preferred_time.minute,
#                     day_of_week=f'*/{search.frequency_days}'
#                 ),
#                 "args": (search.source_websites),
#             }
#         return schedules
#     finally:
#         db.close()
#
#
# app.conf.beat_schedule = get_dynamic_schedule()

# TODO: Check erro in Celery Beat Container - see the logs
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
