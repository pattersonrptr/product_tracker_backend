from celery import Celery, group
from celery.schedules import crontab
from scrapers.olx.scraper import Scraper
import os
import time
import random

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")

app = Celery(
    main='scrapers',
    broker=broker_url,
    backend='redis://redis:6379/0'
)

@app.task(name="scrapers.tasks.run_scraper")
def run_scraper(search):
    sleep_time = random.uniform(5, 25)
    time.sleep(sleep_time)
    print(f"RUNNING SCRAPER WITH {search} (slept for {sleep_time:.2f}s)")
    Scraper().run(search=search)
    return f"Done with {search} (slept for {sleep_time:.2f}s)"

@app.task(name="scrapers.tasks.run_scrapers")
def run_scrapers():
    searches = ["livro python", "livro java", "livro javascript"]
    # Cria um grupo de tarefas para processamento paralelo
    return group(run_scraper.s(search) for search in searches)()

app.conf.beat_schedule = {
    'run_scrapers_daily': {
        'task': 'scrapers.tasks.run_scrapers',
        'schedule': crontab(hour="0", minute="0"),  # Meia-noite UTC
    },
}

app.conf.timezone = 'UTC'
