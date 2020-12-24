
import requests
from lxml import etree
from lxml import html
import urllib.parse
from item_scrapper.SiteScrappers.WebsiteItem import WebsiteItem
from item_scrapper.SiteScrappers.WebsiteScrapper import WebsiteScrapper

class NeweggScrapper(WebsiteScrapper):

    url = "https://www.newegg.com/"
    maximumPagesToGrab = 3
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    }
    itemToSearch = ''

    itemPageXpath = "//div[contains(@class, 'items-grid-view') and not(contains(@class, 'sponsored-brands-items'))]"
    itemElementXpath = ".//div[@id and @class='item-cell']"

    itemPriceXpath = './/li[contains(@class, "price-current")]'
    itemNameXpath = itemLinkXpath = './/a[@class="item-title"]'
    itemPictureXpath = './/img'

    maxRetries = 3

    def initializeScrapper(self, itemToSearch):
        self.itemToSearch = itemToSearch

    def getPossibleItemWebElements(self):
        itemList = []
        itemPageCount = 1

        while True:
            itemsUrl = self.url+"p/pl?d="+urllib.parse.quote(self.itemToSearch)+"&Order=1&page="+str(itemPageCount)
            try:
                # Adding them together because if one fails it just returns an empty list this
                itemsPage = requests.get(itemsUrl, headers=self.headers)

            except Exception as e:
                print("Failed to grab page number "+ str(itemPageCount)+" for Newegg")
                print(e)
                break

            searchItemHtml = html.fromstring(itemsPage.content)

            try:
                adSeperatedSections = searchItemHtml.xpath(self.itemPageXpath)
                for itemsSection in adSeperatedSections:
                    itemList = itemList + itemsSection.xpath(self.itemElementXpath)
            except Exception as e:
                print("Failed to grab the items for page number "+ str(itemPageCount)+" for Newegg")
                print(e)
                break

            itemPageCount += 1
            if itemPageCount > self.maximumPagesToGrab:
                break

        return itemList

    def isValidWebElement(self, itemElement):
        if( len(itemElement.xpath(self.itemPriceXpath+"//strong")) == 0 and len(itemElement.xpath(self.itemPriceXpath+"//sup")) == 0  ):
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
            dollarText = itemElement.xpath(self.itemPriceXpath+"//strong")[0].text
            centsText = itemElement.xpath(self.itemPriceXpath+"//sup")[0].text
            itemPrice = float(dollarText+centsText)
        except Exception as e:
            print("Failure on finding the newegg item Price!")
            print(e)

        itemLink = ""
        try:
            itemLink = self.url+str(itemElement.xpath(self.itemLinkXpath+"/@href")[0])
        except Exception as e:
            print("Failure on finding the newegg item LINK!")
            print(e)

        pictureHtmlLink = ""
        try:
            pictureHtmlLink = etree.tostring(itemElement.xpath(self.itemPictureXpath)[0], pretty_print=True).decode("utf-8")
        except Exception as e:
            print("Exception on finding the newegg item Picture Link!")
            print(e)

        itemName = ""
        try:
            itemName = itemElement.xpath(self.itemNameXpath)[0].text
        except Exception as e:
            print("Exception on finding the newegg item Name")
            print(e)

        fullItem = WebsiteItem()
        fullItem.websiteName = "Newegg"
        fullItem.itemPrice = itemPrice
        fullItem.itemName = itemName
        fullItem.itemPictureHtml = pictureHtmlLink
        if( len(itemLink) > 0 ):
            fullItem.itemLink = itemLink

        return fullItem

    def finish(self):
        self.myDriver.quit()