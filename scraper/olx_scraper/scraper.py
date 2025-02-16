from backend.services.database_manager import DatabaseManager
from scraper.olx_scraper.webdriver import WebDriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import time
import random

class Scraper():
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.driver = WebDriver().getDriver()
    
    def run(self):
        try:
            self.searchScreen()
            self.doResearch("livro java")
            links = self.captureItemLinks()
            items = self.getItemsData(links)

            for item in items:
                self.db_manager.save_ad(
                    url=item['url'],
                    title=item['title'],
                    price=item['price']
                )
                print(item)

        except Exception as ex:
            print(ex)
        finally:
            self.driver.quit()
    
    def closeModalIfExists(self):
        try:
            close_modal_button = self.driver.find_element(
                By.CLASS_NAME,
                "olx-modal__close-button"
            )
            close_modal_button.click()
            print("Modal fechado.")
        except NoSuchElementException:
            print("Modal não encontrado.")
    
    def searchScreen(self):
        self.driver.get("https://www.olx.com.br/")
        self.driver.maximize_window()
        time.sleep(random.uniform(5, 10))

        self.closeModalIfExists()

        time.sleep(random.uniform(3, 6))
    
    def doResearch(self, researchKey):
        search_input = self.driver.find_element(
            By.CLASS_NAME, "olx-text-input__input-field"
        )
        search_input.send_keys(researchKey)
        time.sleep(random.uniform(5, 10))
        search_input.send_keys(Keys.ENTER)

        time.sleep(random.uniform(5, 10))

    def getResultPagesCount(self):
        pass
    
    def nextResultPage(self):
        pass

    def captureItemLinks(self):
        ad_links = []
        try:
            ads = self.driver.find_elements(By.CLASS_NAME, "olx-ad-card__link-wrapper")
            for ad in ads:
                link = ad.get_attribute("href")
                if link:
                    ad_links.append(link)
        except NoSuchElementException:
            print("Nenhum anúncio encontrado.")
        
        return ad_links
    
    def getItemsData(self, ad_links):
        items = []
        for i, link in enumerate(ad_links[:5]):
            self.driver.quit()
            self.driver = WebDriver().getDriver()

            print(f"Acessando anúncio {i + 1}: {link}")
            
            items.append(
                self.getItemData(i, link)
            )
            time.sleep(random.uniform(5, 7))
        return items

    def getItemData(self, item_number, link):
        self.driver.get(link)
        time.sleep(random.uniform(5, 10))
        try:
            title_element = self.driver.find_element(
                By.CSS_SELECTOR,
                "h1[data-ds-component='DS-Text'].ad__sc-45jt43-0"
            )
            title = title_element.text
        except NoSuchElementException:
            title = "Título não encontrado"

        try:
            price_element = self.driver.find_element(
                By.CSS_SELECTOR,
                "h2.olx-text:nth-child(2)"
            )
            price = price_element.text.replace("R$ ", "")
        except NoSuchElementException:
            price = "Preço não encontrado"

        print("Number: ", item_number)
        print("Title: ", title)
        print("Price: ", price)

        return {
            "url": link,
            "title": title,
            "price": price,
        }
