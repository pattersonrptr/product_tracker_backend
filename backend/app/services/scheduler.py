from apscheduler.schedulers.background import BackgroundScheduler
from app.services.scraper import OLXScraper
from app.services.notifications import send_price_alert

scheduler = BackgroundScheduler()

def daily_scrape():
    scraper = OLXScraper()
    scraper.scrape_and_update()

scheduler.add_job(daily_scrape, 'cron', hour=8)
scheduler.start()
