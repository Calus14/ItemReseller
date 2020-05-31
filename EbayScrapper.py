# import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
# from threading import Thread

class EbayWebScrapper:

    url = "https://www.ebay.com/"
    inputSearchElementXpath = "//input[class='gh-tb ui-autocomplete-input']"
    searchButtonElementXpath = "//input[type='submit'][class='btn btn-prim gh-spr'][id='gh-btn'][value='Search']"
    listDisplayElementXpath = "//ul[class='srp-river-results']"
    itemElementXpath = "/li[class='s-item']"


    def __init__(self):
        self.myDriver = webdriver.Chrome(ChromeDriverManager().install())
        print("current session is "+self.myDriver.session_id)
        self.myDriver.get(self.url)
        print("Initializted self")

    def search(self, searchText):
        print("Entering in the search info of "+searchText)
        try:
            self.myDriver.find_element_by_xpath(self.inputSearchElementXpath).sendKeys(searchText)
            self.myDriver.find_element_by_xpath(self.searchButtonElementXpath).click()
        except NoSuchElementException as e:
            print(e)
            print("Failed to enter into the text box and press the button")

        try:
            itemElement = self.myDriver.find_element_by_xpath(self.listDisplayElementXpath)
        except NoSuchElementException as e:
            print(e)
            print("Could not find the element that contained all items")

        try:
            allItems = itemElement.find_elements_by_xpath(self.itemElementXpath)
        except NoSuchElementException as e:
            print(e)
            print("Individual elements fails")

        print(allItems)

    def finish(self):
        self.myDriver.close()


