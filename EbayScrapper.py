import time
import collections
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
# from threading import Thread

class EbayWebScrapper:

    url = "https://www.ebay.com/"
    inputSearchElementXpath = "//input[@class='gh-tb ui-autocomplete-input']"
    searchButtonElementXpath = "//input[@type='submit'][@class='btn btn-prim gh-spr'][@id='gh-btn'][@value='Search']"
    listDisplayElementXpath = "//ul[@class='srp-results srp-grid clearfix']"
    itemElementXpath = "//*[@id='srp-river-results']//ul//li[@class='s-item    '][@data-view='mi:1686|iid:"
    itemPriceXpath = "//span[@class='s-item__price']"
    itemNameXpath = "//h3"
    maxRetries = 3


    def __init__(self):
        self.myDriver = webdriver.Chrome(ChromeDriverManager().install())
        self.myDriver.get(self.url)
        print("Initializted ebay Scrapper")

    def priceSearch(self, searchText):

        header = self.myDriver.find_element_by_tag_name("header")
        try:
            searchBox = header.find_element_by_xpath(self.inputSearchElementXpath)
            searchBox.send_keys(searchText)
            searchButton = header.find_element_by_xpath(self.searchButtonElementXpath)
            searchButton.click()
        except NoSuchElementException as e:
            print(e)
            print("Failed to enter into the text box and press the button")

        #Re get the header cause the page will have reloaded
        header = self.myDriver.find_element_by_tag_name("header")
        #allItems = header.find_elements_by_xpath(self.itemElementXpath)
        time.sleep(4)

        #print(len(allItems))

        itemNamePriceDict = {}
        for num in range(1, 60):
            for tries in range(self.maxRetries):
                try:
                    itemSpecificString = self.itemElementXpath+str(num)+"']"

                    price = float(header.find_element_by_xpath(itemSpecificString+self.itemPriceXpath).text.split(" to ")[0][1:])
                    name = header.find_element_by_xpath(itemSpecificString+self.itemNameXpath).text

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


