import time
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
# from threading import Thread
from item_scrapper.SiteScrappers.WebsiteItem import WebsiteItem
from item_scrapper.SiteScrappers.WebsiteScrapper import WebsiteScrapper


class EbayWebScrapper(WebsiteScrapper):

    url = "https://www.ebay.com/"
    inputSearchElementXpath = "//input[@class='gh-tb ui-autocomplete-input']"
    searchButtonElementXpath = "//input[@type='submit'][@class='btn btn-prim gh-spr'][@id='gh-btn'][@value='Search']"

    itemPageXpath = "//ul[@class]"
    itemElementXpath = "//li[@class='s-item    '][@data-view]"
    itemElementXpathAlternative = "//li[@class='s-item    s-item--watch-at-corner'][@data-view]"

    itemPriceHtml = '<span class="s-item__price">'

    itemNameHtml = '<h3 class="s-item__title">'

    itemLinkHtml = '<a .* class="s-item__link" href='
    itemPictureHtml = '<div class="s-item__image-helper"></div>'

    maxRetries = 3

    def initializeScrapper(self):
        self.myDriver = webdriver.Chrome(ChromeDriverManager().install())
        self.myDriver.get(self.url)
        print("Initializted ebay Scrapper")

    def enterItemSearch(self, itemToSearch):
        header = self.myDriver.find_element_by_tag_name("header")
        try:
            searchBox = header.find_element_by_xpath(self.inputSearchElementXpath)
            searchBox.send_keys(itemToSearch)
            searchButton = header.find_element_by_xpath(self.searchButtonElementXpath)
            searchButton.click()
        except NoSuchElementException as e:
            print(e)
            print("Failed to enter into the text box and press the button")
            return

    def getPossibleItemWebElements(self):
        for tries in range(self.maxRetries):
            try:
                itemList = self.myDriver.find_elements_by_xpath(self.itemPageXpath+self.itemElementXpath)
                if len(itemList) == 0:
                    itemList = self.myDriver.find_elements_by_xpath(self.itemPageXpath+self.itemElementXpathAlternative)
                print("Ebay list size")
                print(len(itemList))
                return itemList

            except Exception as e:
                print(e)
                time.sleep(1)

        return None

    def isValidWebElement(self, webElement):
        itemHtml = webElement.get_attribute("innerHTML")
        if( not self.itemPriceHtml in itemHtml or not self.itemNameHtml in itemHtml or not self.itemPictureHtml in itemHtml ):
            return False
        return True

    def getItemFromWebElement(self, webElement):
        itemHtml = webElement.get_attribute("innerHTML")

        priceStartIndex = itemHtml.find(self.itemPriceHtml) + len(self.itemPriceHtml)
        priceEndIndex = priceStartIndex + itemHtml[priceStartIndex:].find("</span>")
        itemPrice = -1.0
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

        pictureHtmlLink = ""
        pictureMatch = re.search(self.itemPictureHtml, itemHtml)
        if( pictureMatch ):
            pictureStartIndex = pictureMatch.end(0)
            pictureEndIndex = pictureStartIndex + itemHtml[pictureStartIndex:].find("</div>")
            pictureHtmlLink = itemHtml[pictureStartIndex:pictureEndIndex]
            print("Found Picture link with html "+pictureHtmlLink)

        nameStartIndex = itemHtml.find(self.itemNameHtml) + len(self.itemNameHtml)
        nameEndIndex = nameStartIndex + itemHtml[nameStartIndex:].find("</h3>")
        itemName = itemHtml[nameStartIndex:nameEndIndex]
        #Replace any bolding of the name or other weird shit
        itemName = re.sub('<[^>]*>', '', itemName)

        fullItem = WebsiteItem()
        fullItem.websiteName = "Ebay"
        fullItem.itemPrice = itemPrice
        fullItem.itemName = itemName
        fullItem.itemPictureHtml = pictureHtmlLink
        if( len(itemLink) > 0 ):
            fullItem.itemLink = itemLink

        return fullItem

    def finish(self):
        self.myDriver.quit()


