from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService

class WebDriver:
    def __init__(self, browser='chrome', driver_path=None):
        self.browser = browser.lower()
        self.driver_path = driver_path
        self.options = None
        self.driver = None
        self.setDriver()
    
    def setOptions(self):
        if self.browser == 'chrome':
            from selenium.webdriver.chrome.options import Options
            self.options = Options()
            # Configurações específicas do Chrome
            self.options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        elif self.browser == 'firefox':
            from selenium.webdriver.firefox.options import Options
            self.options = Options()
            # Configurações específicas do Firefox
            self.options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            self.options.set_preference("network.http.phishy-userpass-length", 255)
        else:
            raise ValueError(f"Navegador não suportado: {self.browser}")
    
    def setDriver(self):
        self.setOptions()
        
        if self.browser == 'chrome':
            service = ChromeService(self.driver_path) if self.driver_path else ChromeService()
            self.driver = webdriver.Chrome(service=service, options=self.options)
        elif self.browser == 'firefox':
            service = FirefoxService(self.driver_path) if self.driver_path else FirefoxService()
            self.driver = webdriver.Firefox(service=service, options=self.options)
        else:
            raise ValueError(f"Navegador não suportado: {self.browser}")
    
    def getDriver(self):
        return self.driver