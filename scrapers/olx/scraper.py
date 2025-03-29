import os
import time
import random
import logging
import requests     # TODO: check if requests is still needed
import cloudscraper
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

from app.models import Product


class Scraper:
    def __init__(self, api_url=None):
        self.BASE_URL = "https://www.olx.com.br/brasil"
        self.session = cloudscraper.create_scraper()
        env_api_url = os.getenv("API_URL", "")
        self.api_url = api_url or (env_api_url if env_api_url else "web:8000")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'DNT': '1',
            'Sec-GPC': '1',
        }
        self.timeouts = (5, 15)  # (connect, read)
        self.session.headers.update(self.headers)

    def scrape_search(self, search_term):
        page_number = 1
        has_next = True
        all_links = []

        while has_next:
            try:
                search_url = self._build_search_url(search_term, page_number)
                html = self._safe_request(search_url)

                if not html:
                    break

                links = self._extract_links(html)

                if not links:
                    break

                all_links.extend(links)
                print(f"Links collected: {len(all_links)}")
                page_number += 1

            except Exception as e:
                print(f"Error on page {page_number}: {str(e)}")
                break

        return all_links

    def scrape_product_page(self, url):
        html = self._safe_request(url)
        title = None
        price = None

        if html:
            soup = BeautifulSoup(html, 'html.parser')
            title = self._extract_title(soup)
            price = self._extract_price(soup)

        return {
            'url': url,
            'title': title,
            'price': price,
        }

    def update_product(self, product: dict):
        url = product['url']
        html = self._safe_request(url)
        title = None
        price = None

        if html:
            soup = BeautifulSoup(html, 'html.parser')
            title = self._extract_title(soup)
            price = self._extract_price(soup)

        return {
            'id': product['id'],
            'url': url,
            'title': title,
            'price': price,
        }

    def _build_search_url(self, search_term, page_number=1):
        encoded_search = quote_plus(search_term)
        return f"{self.BASE_URL}?q={encoded_search}&o={page_number}"

    def _safe_request(self, url, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    url,
                    timeout=self.timeouts,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response.text

            except requests.exceptions.HTTPError as e:
                status_code = getattr(e.response, 'status_code', 'unknown')
                print(f"HTTP error {status_code} em {url}")
            except requests.exceptions.RequestException as e:
                print(f"Connection error: {str(e)}")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")

            if attempt < max_retries - 1:
                sleep_time = random.uniform(2, 5) * (attempt + 1)
                print(f"Trying again in {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)

        print(f"Failed after {max_retries} attempts for {url}")
        return None

    def _extract_links(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []

        for a in soup.select('section.olx-ad-card--horizontal > a'):
            href = a.get('href', '').split('#')[0]
            if href and href not in links:
                links.append(href)

        return links

    def _extract_title(self, soup):
        try:
            return soup.find('span', {'class': 'olx-text--title-medium'}).get_text(strip=True)
        except AttributeError:
            return "Title not found"

    def _extract_price(self, soup):
        try:
            price_text = soup.find(
                'span', {'class': 'olx-text olx-text--title-large olx-text--block'}
            ).get_text(strip=True)
            return price_text.replace('R$', '').strip()
        except AttributeError:
            return "Price not found"

    def _send_to_api(self, items):
        if not items:
            logging.warning("No items to send")
            return

        success_count = 0
        for item in items:
            try:
                response = requests.post(
                    f"{self.api_url}/products/",
                    json=item,
                    timeout=10
                )
                if response.status_code == 201:
                    success_count += 1
                else:
                    title = item.get('title', 'Unknown Item')
                    logging.error(f"Error sending {title}: {response.status_code} - {response.text}")
            except Exception as e:
                logging.error(f"Send failure: {str(e)}")

        logging.info(f"Submission complete: {success_count}/{len(items)} saved items")
