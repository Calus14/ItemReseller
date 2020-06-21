import time
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
# from threading import Thread

class EbayWebScrapper:

    url = "https://www.ebay.com/"
    inputSearchElementXpath = "//input[@class='gh-tb ui-autocomplete-input']"
    searchButtonElementXpath = "//input[@type='submit'][@class='btn btn-prim gh-spr'][@id='gh-btn'][@value='Search']"

    itemPageXpath = "//ul[@class]"
    itemElementXpath = "//li[@class='s-item    '][@data-view]"
    itemElementXpathAlternative = "//li[@class='s-item    s-item--watch-at-corner'][@data-view]"

    itemPriceHtml = '<span class="s-item__price">'

    itemNameHtml = '<h3 class="s-item__title">'

    itemLinkHtml = '<a .* class="s-item__link" href='

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

        #Gaurentee that it loads the new page source correctly
        time.sleep(3)

        #List Of all the Items on the page
        itemList = []
        #Dictionary from name to meta data about the item (price/link/etc) that will be sorted
        itemDict = {}

        for tries in range(self.maxRetries):
            try:
                itemList = self.myDriver.find_elements_by_xpath(self.itemPageXpath+self.itemElementXpath)
                if len(itemList) is 0:
                    itemList = self.myDriver.find_elements_by_xpath(self.itemPageXpath+self.itemElementXpathAlternative)
                print("Ebay list size")
                print(len(itemList))

                break

            except Exception as e:
                print(e)
                time.sleep(1)

        for itemWebElement in itemList:
            itemHtml = itemWebElement.get_attribute("innerHTML")
            if( not self.itemPriceHtml in itemHtml or not self.itemNameHtml in itemHtml ):
                continue

            priceStartIndex = itemHtml.find(self.itemPriceHtml) + len(self.itemPriceHtml)
            priceEndIndex = priceStartIndex + itemHtml[priceStartIndex:].find("</span>")
            try:
                itemPrice = float( itemHtml[priceStartIndex:priceEndIndex].replace(',', '').replace('$', '') )
            except Exception as e:
                # on Ebay there is a possibility of <low> to <high>
                try:
                    priceEndIndex = priceStartIndex + itemHtml[priceStartIndex:].find("<span class")
                    itemPrice = float( itemHtml[priceStartIndex:priceEndIndex].replace(',', '').replace('$', '') )
                except Exception as e2:
                    print("Was unable to find the valid price end index expected it to be price to price2 format")


            itemLink = ""
            if( re.search(self.itemLinkHtml, itemHtml) ):
                matchObj = re.search(self.itemLinkHtml, itemHtml)
                linkStartIndex = matchObj.end(0)
                linkEndIndex = linkStartIndex + itemHtml[linkStartIndex:].find(">")
                itemLink = itemHtml[linkStartIndex:linkEndIndex].replace('"', '')

            nameStartIndex = itemHtml.find(self.itemNameHtml) + len(self.itemNameHtml)
            nameEndIndex = nameStartIndex + itemHtml[nameStartIndex:].find("</h3>")
            itemName = itemHtml[nameStartIndex:nameEndIndex]
            #Replace any bolding of the name or other weird shit
            itemName = re.sub('<[^>]*>', '', itemName)

            itemDict[itemName] = [itemPrice, itemLink]

        print("Ebay")
        print( len(itemDict) )
        return itemDict

    def finish(self):
        self.myDriver.quit()


