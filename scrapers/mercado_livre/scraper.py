import cloudscraper

from bs4 import BeautifulSoup
from cloudscraper import requests

from scrapers.base.scraper import Scraper


class MercadoLivreScraper(Scraper):
    def __init__(self):
        self.BASE_URL = "https://lista.mercadolivre.com.br"

        self.session = cloudscraper.create_scraper()
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        }
        self.session.headers.update(self.headers)

    def _extract_links(self, html: str) -> list:
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for a in soup.select(".poly-component__title-wrapper a"):
            href = a.get("href", "")
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

    def _get_next_url(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        next_button = soup.select_one(
            "li.andes-pagination__button--next a.andes-pagination__link"
        )

        if next_button and next_button.has_attr("href"):
            next_url = next_button["href"]
            return next_url

        return ""

    def search(self, search_term: str) -> list:
        page_number = 1
        has_next = True
        all_links = []
        search_url = f"{self.BASE_URL}/{search_term}"

        while has_next:
            try:
                html = self._make_request(search_url)

                if not html:
                    break

                links = self._extract_links(html)

                if not links:
                    break

                all_links.extend(links)
                page_number += 1
                print(f"Page Number {page_number}")
                search_url = self._get_next_url(html)

            except Exception as e:
                print(f"Error on page {page_number}: {str(e)}")
                print(f"Search URL: {search_url}")
                break

        return all_links

    def scrape_data(self, url: str) -> dict:
        html = self._make_request(url)
        soup = BeautifulSoup(html, "html.parser")
        title = self._extract_title(soup)
        price = self._extract_price(soup)

        return {
            "title": title,
            "url": url,
            "price": price,
        }

    def _extract_price(self, soup):
        price_element = soup.find("meta", itemprop="price")
        price = (
            price_element["content"]
            if price_element and "content" in price_element.attrs
            else ""
        )
        return price

    def _extract_title(self, soup):
        title_element = soup.find("h1", class_="ui-pdp-title")
        title = title_element.get_text(strip=True) if title_element else ""
        return title

    def update_data(self, product: dict) -> dict:
        data = self.scrape_data(product["url"])
        return {**product, **data}

    def __str__(self):
        return "Mercado Livre Scraper"
