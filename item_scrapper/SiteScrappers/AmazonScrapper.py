import time
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from item_scrapper.SiteScrappers.WebsiteItem import WebsiteItem
from item_scrapper.SiteScrappers.WebsiteScrapper import WebsiteScrapper


class AmazonScrapper(WebsiteScrapper):

    url = "https://www.amazon.com/"

    searchBoxXpath = "//*[@id='twotabsearchtextbox']"
    searchButtonXpath = "//header/div/div[@id='nav-belt']/div[@class='nav-fill']/div/form/div[@class='nav-right']/div/input"

    itemPageXpath = "//div[@class='s-main-slot s-result-list s-search-results sg-row']"
    itemXpath = "//div[@data-index]"

    itemDollarHtml = '<span class="a-price-whole">'
    itemDecimalHtml= '<span class="a-price-decimal">'
    itemCentsHtml = '<span class="a-price-fraction">'

    itemLinkHtml = '<a class=".* a-link-normal .*" href='

    itemNameHtml = '<span class=".* a-text-normal" dir="auto">'

    itemPictureHtml = '<div class="a-section aok-relative s-image.*">'

    def initializeScrapper(self):
        self.myDriver = webdriver.Chrome(ChromeDriverManager().install())
        self.myDriver.get(self.url)
        print("Initializted Amazon Scrapper")


    def enterItemSearch(self, itemToSearch):
        try:
            searchBox = self.myDriver.find_element_by_xpath(self.searchBoxXpath)
            searchBox.send_keys(itemToSearch)
            searchButton = self.myDriver.find_element_by_xpath(self.searchButtonXpath)
            searchButton.click()
        except NoSuchElementException as e:
            print(e)
            print("Failed to enter into the text box and press the button")
            return

    def getPossibleItemWebElements(self):
        #Only look at the first page
        for tries in range(self.maxRetries):
            try:
                itemList = self.myDriver.find_elements_by_xpath(self.itemPageXpath+self.itemXpath)
                print("Amazon list size")
                print(len(itemList))
                return itemList

            except Exception as e:
                print(e)
                time.sleep(1)
        return None

    def isValidWebElement(self, webElement):
        itemHtml = webElement.get_attribute("innerHTML")

        if( not self.itemDollarHtml in itemHtml or not self.itemDecimalHtml in itemHtml or not re.search(self.itemNameHtml, itemHtml) ):
            return False
        return True

    def getItemFromWebElement(self, webElement):
        itemHtml = webElement.get_attribute("innerHTML")
        dollarStartIndex = itemHtml.find(self.itemDollarHtml) + len(self.itemDollarHtml)
        dollarEndIndex = itemHtml.find(self.itemDecimalHtml)

        dollarAmount = float( itemHtml[dollarStartIndex:dollarEndIndex].replace(',', '').replace('"', '') )

        centsStartIndex = itemHtml.find(self.itemCentsHtml) + len(self.itemCentsHtml)
        centsEndIndex = centsStartIndex + itemHtml[centsStartIndex:].find("</span>")
        centsAmount = float( itemHtml[centsStartIndex:centsEndIndex].replace('"', '') )

        itemLink = ""
        matchObj = re.search(self.itemLinkHtml, itemHtml)
        if( matchObj ):
            linkStartIndex = matchObj.end(0)
            linkEndIndex = linkStartIndex + itemHtml[linkStartIndex:].find(">")
            itemLink = itemHtml[linkStartIndex:linkEndIndex].replace('"', '')

        pictureHtmlLink = ""
        pictureMatch = re.search(self.itemPictureHtml, itemHtml)
        if( pictureMatch ):
            pictureStartIndex = pictureMatch.end(0)
            pictureEndIndex = pictureStartIndex + itemHtml[pictureStartIndex:].find(">")+1
            pictureHtmlLink = itemHtml[pictureStartIndex:pictureEndIndex].replace('\n', '')
            print("Found Picture link with html "+pictureHtmlLink)

        nameMatch = re.search(self.itemNameHtml, itemHtml)
        nameStartIndex = nameMatch.end(0)
        nameEndIndex = nameStartIndex + itemHtml[nameStartIndex:].find("</span>")
        itemName = itemHtml[nameStartIndex:nameEndIndex]

        fullItem = WebsiteItem()
        fullItem.websiteName = "Amazon"
        fullItem.itemName = itemName
        fullItem.itemPrice = dollarAmount+(centsAmount/100)
        fullItem.itemPictureHtml = pictureHtmlLink
        if(len(itemLink) > 0):
            fullItem.itemLink = itemLink

        return fullItem


    def finish(self):
        self.myDriver.quit()