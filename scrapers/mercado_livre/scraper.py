import cloudscraper

from bs4 import BeautifulSoup
from cloudscraper import requests
from urllib.parse import quote_plus

from scrapers.base.scraper import Scraper


class MercadoLivreScraper(Scraper):
    def __init__(self):
        self.BASE_URL = "https://lista.mercadolivre.com.br"
        self.session = cloudscraper.create_scraper()
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        }
        self.session.headers.update(self.headers)
        
    def _extract_links(self, html: str) -> list:
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for a in soup.select('.poly-component__title-wrapper a'):
            href = a.get('href', '')
            if not href.startswith("https://click1"):
                links.append(href)

        return links
    
    def _make_request(self, url: str) -> str:
        try:
            response = self.session.get(url, allow_redirects=True)
            response.raise_for_status()
            return response.text

        except requests.exceptions.HTTPError as e:
            status_code = getattr(e.response, "status_code", "unknown")
            print(f"HTTP error {status_code} em {url}")

        except requests.exceptions.RequestException as e:
            print(f"Connection error: {str(e)}")

        except Exception as e:
            print(f"Unexpected error: {str(e)}")

        return ""
    
    def search(self, search_term: str) -> List[str]:       
        search_url = f'{self.BASE_URL}/{search_term}'
        resp = self._make_request(url)

        return self._extract_links(resp.content)
    
    def scrape_data(self, url: str) -> dict:
        response = self._make_request(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        title_element = soup.find('h1', class_='ui-pdp-title')
        title = title_element.get_text(strip=True) if title_element else ''

        price_element = soup.find('meta', itemprop='price')
        price = price_element['content'] if price_element and 'content' in price_element.attrs else ''

        return {
            "title": title,
            "url": response.url,
            "price": price,
        }

    def update_data(self, product: dict) -> dict:
        data = scrape_data(url)
        return {**product, **data}

