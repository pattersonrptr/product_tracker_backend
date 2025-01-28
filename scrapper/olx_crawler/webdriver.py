from selenium import webdriver



class WebDriver:
    def __init__(self):
        self.setOptions()
        self.setDriver()
    
    def setOptions(self):
        self.options = webdriver.FirefoxOptions()
        self.options.set_preference(
            "general.useragent.override",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

    def setDriver(self):
        self.driver = webdriver.Firefox(options=self.options)

    def getDriver(self):
        return self.driver
