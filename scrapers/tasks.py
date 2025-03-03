from celery import Celery
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
    Scraper().run()

    return f"Done with {search} (slept for {sleep_time:.2f}s)"

#TODO:
# Criar uma task que chama run_scraper em loop, passando todos os search_tearms
# Não vou agendar uma task para cada team, mas posso agendar uma que dispara várias

# TODO:
#  precisa ter o CHROME ou o FIREFOX e o CHROMEDRIVER ou o GECKODRIVER instalados para rodar o scraper



app.conf.beat_schedule = {
    'run_scraper_every_60_seconds': {
        'task': 'scrapers.tasks.run_scraper',
        'schedule': 60.0,
        'args': ("java",),
    },
    # 'run_scraper_midnight': {
    #     'task': 'scrapers.tasks.run_scraper',
    #     'schedule': crontab(hour=0, minute=0),
    #     'args': ("python",),
    # }
}

app.conf.timezone = 'UTC'
