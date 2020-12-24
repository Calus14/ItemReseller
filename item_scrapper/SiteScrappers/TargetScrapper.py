import requests
#from requests_html import HTMLSession
from lxml import etree
from lxml import html
import urllib.parse
from item_scrapper.SiteScrappers.WebsiteItem import WebsiteItem
from item_scrapper.SiteScrappers.WebsiteScrapper import WebsiteScrapper

#Target is weird and old and relies on javascript serverside to render the full html so we will need to invoke
# the requests-HTML library which is supposed to render the javascript from the DOM so we can get the full html/
class TargetScrapper(WebsiteScrapper):

    url = "https://www.target.com/"
    maximumPagesToGrab = 3
    itemToSearch = ''

    searchedItemHtml = None

    #Target sucks to scrape, it has an auto generated row id and like 10 different unordered list elements. For now the assumption
    # is that the http request will return the elements with a h-padding-t-tight to identify which is the unique item Page.
    itemPageXpath = '//ul[contains(@class, "Row-") and contains(@class, "h-padding-t-tight")]'
    #Target also includes random empty items in the searches sometimes... these lack the h-display-flex because they are empty list elements
    itemElementXpath = '/li[contains(@class, "h-display-flex")]'

    #text property on the element
    itemPriceXpath = './/span[@data-test="product-price"]'
    #text property on the element and the item link is the href property
    itemNameXpath = itemLinkXpath = './/a[@data-test="product-title"]'
    #hidden in a div/picture then in one of 4 source elements so just grab the first one and get its srcset property
    itemPictureXpath = './/div[@data-test="product-image"]//source'

    maxRetries = 3

    def initializeScrapper(self, itemToSearch):
        self.itemToSearch = itemToSearch

    def getPossibleItemWebElements(self):
        itemList = []
        itemsCount = 0
        itemPageCount = 1
        #session = HTMLSession()
        while True:
            itemsUrl = self.url+"s?searchTerm="+urllib.parse.quote(self.itemToSearch)
            try:
                requestsResult = requests.get(itemsUrl)
            except Exception as requestsException:
                print("Stopped trying to get pages for Target at page "+str(itemPageCount))
                print(requestsException)
                break

            searchedItemHtml = html.fromstring(requestsResult.content)
            htmlset = etree.tostring(searchedItemHtml, pretty_print=True).decode("utf-8")
            print(htmlset)

            try:
                itemList = itemList + searchedItemHtml.xpath("//ul")
                for item in itemList:
                    testHtml = etree.tostring( item, pretty_print=True).decode("utf-8")
                    print(testHtml)
            except Exception as e:
                print("Failed to find a list of items for Target on page "+str(itemPageCount))
                print(e)
                break

            itemsCount = len(itemList)
            itemPageCount += 1
            if itemPageCount >= self.maximumPagesToGrab:
                break

        return itemList

    def isValidWebElement(self, itemElement):
        if( len(itemElement.xpath(self.itemPriceXpath)) == 0  ):
            return False
        if( len(itemElement.xpath(self.itemNameXpath)) == 0  ):
            return False
        if( len(itemElement.xpath(self.itemPictureXpath)) == 0  ):
            return False
        if( len(itemElement.xpath(self.itemLinkXpath)) == 0  ):
            return False
        return True

    def getItemFromWebElement(self, itemElement):

        itemPrice = None
        try:
            itemPriceText = itemElement.xpath(self.itemPriceXpath)[0].text
            itemPrice = float( itemPriceText.replace(',', '').replace('$', '') )
        except Exception as e:
            print("Failure on finding the Target item PRICE!")
            print(e)

        itemLink = ""
        try:
            itemLink = self.url+str(itemElement.xpath(self.itemLinkXpath+"/@href")[0])
        except Exception as e:
            print("Failure on finding the Target item LINK!")
            print(e)

        pictureHtmlLink = ""
        try:
            pictureHtmlLink = "<img class=\"itemImage\" data-image-src=\""+itemElement.xpath(self.itemPictureXpath+"/@srcset")[0]+"\">"
        except Exception as e:
            print("Exception on finding the Target item Picture Link!")
            print(e)

        itemName = ""
        try:
            itemName = itemElement.xpath(self.itemNameXpath)[0].text
        except Exception as e:
            print("Exception on finding the item NAME")
            print(e)

        fullItem = WebsiteItem()
        fullItem.websiteName = "Target"
        fullItem.itemPrice = itemPrice
        fullItem.itemName = itemName
        fullItem.itemPictureHtml = pictureHtmlLink
        if( len(itemLink) > 0 ):
            fullItem.itemLink = itemLink

        return fullItem

    def finish(self):
        self.myDriver.quit()