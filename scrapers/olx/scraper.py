import cloudscraper

from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from cloudscraper import requests

from scrapers.base.scraper import Scraper


class OLXScraper(Scraper):
    def __init__(self):
        self.BASE_URL = "https://www.olx.com.br/brasil"
        self.session = cloudscraper.create_scraper()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "DNT": "1",
            "Sec-GPC": "1",
        }
        self.session.headers.update(self.headers)

    def _build_search_url(self, search_term, page_number=1):
        encoded_search = quote_plus(search_term)
        return f"{self.BASE_URL}?q={encoded_search}&o={page_number}"

    def _extract_links(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        links = []

        for a in soup.select("section.olx-ad-card--horizontal > a"):
            href = a.get("href", "").split("#")[0]
            if href and href not in links:
                links.append(href)

        return links

    def _extract_title(self, soup):
        try:
            return soup.find("span", {"class": "olx-text--title-medium"}).get_text(
                strip=True
            )
        except AttributeError:
            return "Title not found"

    def _extract_price(self, soup):
        try:
            price_text = soup.find(
                "span", {"class": "olx-text olx-text--title-large olx-text--block"}
            ).get_text(strip=True)
            return price_text.replace("R$", "").strip()
        except AttributeError:
            return "Price not found"

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

    def search(self, search_term: str) -> list[str]:
        page_number = 1
        has_next = True
        all_links = []
        search_url = self._build_search_url(search_term, page_number)

        while has_next:
            try:
                html = self._make_request(search_url)

                if not html:
                    break

                links = self._extract_links(html)

                if not links:
                    break

                all_links.extend(links)
                # print(f"Links collected: {len(all_links)}")
                page_number += 1

            except Exception as e:
                print(f"Error on page {page_number}: {str(e)}")
                print(search_url)
                break

        return all_links

    def scrape_data(self, url: str) -> dict:
        html = self._make_request(url)
        title = None
        price = None

        if html:
            soup = BeautifulSoup(html, "html.parser")
            title = self._extract_title(soup)
            price = self._extract_price(soup)

        return {
            "source": "olx",
            "url": url,
            "title": title,
            "price": price,
        }

    def update_data(self, product: dict) -> dict:
        url = product["url"]
        html = self._make_request(url)
        title = None
        price = None

        if html:
            soup = BeautifulSoup(html, "html.parser")
            title = self._extract_title(soup)
            price = self._extract_price(soup)

        return {
            "id": product["id"],
            "url": url,
            "title": title,
            "price": price,
        }

    def __str__(self):
        return "OLX Scraper"
