import cloudscraper
import html
import json

from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from cloudscraper import requests
from typing import List, Dict, Any, Optional

from scrapers.base.scraper import ScraperInterface


class OLXScraper(ScraperInterface):
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

    def _build_search_url(self, search_term: str, page_number: int = 1) -> str:
        encoded_search = quote_plus(search_term)
        return f"{self.BASE_URL}?q={encoded_search}&o={page_number}"

    def _extract_links(self, html_content: str) -> List[str]:
        soup = BeautifulSoup(html_content, "html.parser")
        links = []
        for a in soup.select("section.olx-ad-card--horizontal > a"):
            href = a.get("href", "").split("#")[0]
            if href and href not in links:
                links.append(href)
        return links

    def _extract_json_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        script = soup.find("script", {"id": "initial-data"})
        if not script:
            return {}
        decoded_data = html.unescape(script["data-json"])
        return json.loads(decoded_data).get("ad", {})

    def _make_request(self, url: str) -> str:
        try:
            response = self.session.get(url, allow_redirects=True)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
        return ""

    def search(self, search_term: str) -> List[str]:
        page_number = 1
        has_next = True
        all_links = []
        search_url = self._build_search_url(search_term, page_number)

        while has_next:
            html = self._make_request(search_url)
            if not html:
                break
            links = self._extract_links(html)
            if not links:
                break
            all_links.extend(links)
            page_number += 1
            search_url = self._build_search_url(search_term, page_number)
        return all_links

    def scrape_data(self, url: str) -> Dict[str, Any]:
        html = self._make_request(url)
        soup = BeautifulSoup(html, "html.parser")
        json_data = self._extract_json_data(soup)

        title = json_data.get("subject")
        description = json_data.get("body")
        source_product_code = f"OLX - {json_data.get('listId')}"
        price = json_data.get("priceValue")
        images = json_data.get("images", [])
        image_url = images[0].get("original", "") if images else ""
        seller_name = json_data.get("user", {}).get("name")
        city = json_data.get("location", {}).get("municipality")
        state = json_data.get("location", {}).get("uf")

        condition: Optional[str] = next(
            (
                prop["value"]
                for prop in json_data.get("properties", [])
                if prop["name"] == "hobbies_condition"
            ),
            None,
        )

        return {
            "url": url,
            "title": title,
            "description": description,
            "price": price,
            "image_urls": image_url,
            "source_product_code": source_product_code,
            "seller_name": seller_name,
            "city": city,
            "state": state,
            "condition": condition,
            # TODO: the scraper do not need to know its id in the database. But scrapers_manager.py needs to know it!
            # "source_website_id": 1,
            "source_metadata": json_data.get("properties"),
        }

    def update_data(self, product: Dict[str, Any]) -> Dict[str, Any]:
        data = self.scrape_data(product["url"])
        if "id" in product:
            data["id"] = product["id"]
        return data

    def __str__(self):
        return "OLX Scraper"
