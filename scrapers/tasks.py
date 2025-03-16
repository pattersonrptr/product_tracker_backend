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

SEARCHES = ["livro python", "livro java", "livro javascript"]


@app.task(name="scrapers.tasks.run_olx_scraper_searches")
def run_olx_scraper_searches():
    """Task 1: Dispara uma task para cada termo de busca"""
    return group(run_olx_scraper.s(search) for search in SEARCHES)()


@app.task(name="scrapers.tasks.run_olx_scraper")
def run_olx_scraper(search):
    """Task 2: Executa o scraper para um termo de busca e retorna URLs"""
    sleep_time = random.uniform(5, 25)
    time.sleep(sleep_time)
    print(f"🔎 Buscando termo: {search} (sleep {sleep_time:.2f}s)")

    scraper = Scraper()
    try:
        urls = scraper.scrape_search(search)
        # Chama a Task 3 ASSINCRONAMENTE com os resultados
        # TODO: aqui sempre passa success, talvez não seja bom chamar aqui dentro do try, mas depois dele
        process_url_list.apply_async(args=[{"status": "success", "search": search, "urls": urls}])
        return {"status": "success", "search": search, "urls": urls}
    except Exception as e:
        return {"status": "error", "search": search, "message": str(e)}


@app.task(name="scrapers.tasks.process_url_list")
def process_url_list(result):
    """Task 3: Processa URLs e coordena as Tasks 4 e 5"""
    # TODO: ta sempre recebendo status success, devo passar o error também ou remover isso?
    if result["status"] != "success":
        return f"⚠️ Erro na busca {result['search']}: {result['message']}"

    print(f"📥 Processando {len(result['urls'])} URLs de {result['search']}")

    # Cria um chord com as Tasks 4 e aciona a Task 5 ao final
    return chord(
        scrape_product_page.s(url) for url in result["urls"]
    )(save_products.s())


@app.task(name="scrapers.tasks.scrape_product_page")
def scrape_product_page(url):
    """Task 4: Coleta dados de um produto a partir da URL"""
    sleep_time = random.uniform(1, 3)
    time.sleep(sleep_time)
    print(f"🛒 Scraping URL: {url} (sleep {sleep_time:.2f}s)")

    scraper = Scraper()
    try:
        product_data = scraper.scrape_product_page(url)
        return {"status": "success", "data": product_data}
    except Exception as e:
        return {"status": "error", "url": url, "message": str(e)}


@app.task(name="scrapers.tasks.save_products")
def save_products(results):
    """Task 5: Salva produtos no banco via API"""
    successful = [r["data"] for r in results if r["status"] == "success"]
    print(f"💾 Salvando {len(successful)} produtos")

    api_url = f"{os.getenv('API_URL', 'web:8000')}/products/"
    created = 0

    for product in successful:
        # Verifica se produto já existe
        response = requests.get(api_url, params={"url": product["url"]})
        if response.status_code == 200 and response.json():
            continue

        # Cria novo produto
        response = requests.post(api_url, json=product, timeout=10)
        if response.status_code == 201:
            created += 1

    return f"✅ {created} novos produtos criados"


app.conf.beat_schedule = {
    'run_olx_scraper_searches_daily': {
        'task': 'scrapers.tasks.run_olx_scraper_searches',
        'schedule': crontab(hour="0", minute="0"),
    },
}

app.conf.timezone = 'UTC'
