import time
import collections
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class AmazonScrapper:

    url = "https://www.amazon.com/"

    searchBoxXpath = "//*[@id='twotabsearchtextbox']"
        #"//header/div/div[@id='nav-belt']/div[@class='nav-fill']/div[@id='nav-search']/form/div[@class='nav-fill']/div[@class='nav-search-field']/div[1]/input"
    searchButtonXpath = "//header/div/div[@id='nav-belt']/div[@class='nav-fill']/div/form/div[@class='nav-right']/div/input"
    itemPageXpath = "//div[@class='s-main-slot s-result-list s-search-results sg-row']"

    itemXpath = "//div[@data-index='"

    itemPriceXpath = "//span[@class='a-price-whole']"
    itemDecimalXpath = "//span[@class='a-price-fraction']"
    itemNameXpath = "//h2[@class='a-size-mini a-spacing-none a-color-base s-line-clamp-2']/a[@class='a-link-normal a-text-normal']/span[@class='a-size-base-plus a-color-base a-text-normal']"

    nextPageXpath = ""
    maxRetries = 3

    def __init__(self):
        self.myDriver = webdriver.Chrome(ChromeDriverManager().install())
        self.myDriver.get(self.url)
        print("Initializted Amazon Scrapper")


    def priceSearch(self, searchItem):

        try:
            searchBox = self.myDriver.find_element_by_xpath(self.searchBoxXpath)
            searchBox.send_keys(searchItem)
            searchButton = self.myDriver.find_element_by_xpath(self.searchButtonXpath)
            searchButton.click()
        except NoSuchElementException as e:
            print(e)
            print("Failed to enter into the text box and press the button")
            return

        time.sleep(4)

        itemNamePriceDict = {}
        for num in range(1, 60):
            for tries in range(self.maxRetries):
                try:
                    itemSpecificString = self.itemPageXpath+self.itemXpath+str(num)+"']"

                    price = float(self.myDriver.find_element_by_xpath(itemSpecificString+self.itemPriceXpath).text+'.'+self.myDriver.find_element_by_xpath(itemSpecificString+self.itemDecimalXpath).text)

                    name = self.myDriver.find_element_by_xpath(itemSpecificString+self.itemNameXpath).text

                    itemNamePriceDict[name] = price
                    time.sleep(3)
                    break
                except Exception as e:
                    print(e)
                    time.sleep(3)

        sortedItems = sorted(itemNamePriceDict.items(), key=lambda item: item[1])
        sortedDict = {}
        for item in sortedItems:
            sortedDict[item[0]] = item[1]

        return sortedDict


    def finish(self):
        self.myDriver.close()