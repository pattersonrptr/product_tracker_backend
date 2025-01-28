# olx-scrapper
Collects product data from OLX.

# Backend

'''
cd backend
alembic upgrade head
uvicorn app.main:app --reload
'''

## Frontend 

'''
cd frontend
npm install
npm start
'''

## Scraper 

'''
python -m scraper.olx_crawler.crawler
'''

# Notas Finais