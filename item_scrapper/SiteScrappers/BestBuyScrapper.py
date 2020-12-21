import re
import requests
from lxml import etree
from lxml import html
import urllib.parse
from item_scrapper.SiteScrappers.WebsiteItem import WebsiteItem
from item_scrapper.SiteScrappers.WebsiteScrapper import WebsiteScrapper

class BestBuyScrapper(WebsiteScrapper):

    itemToSearch = ''
    maximumPagesToGrab = 3
    url = "https://www.bestbuy.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    }

    itemPageXpath = "//ol[@class='sku-item-list']"
    itemElementXpath = "/li[@class='sku-item']"

    itemPriceXpath = './/div[contains(@class, "priceView-hero-price") and contains(@class, "priceView-customer-price")]/span[@aria-hidden="true"]'
    itemNameXpath = itemLinkXpath = './/h4[@class="sku-header"]/a'
    itemPictureXpath = './/img[@class="product-image"]'

    maxRetries = 3

    def initializeScrapper(self, itemToSearch):
        self.itemToSearch = itemToSearch


    def getPossibleItemWebElements(self):

        itemList = []
        itemPageCount = 1

        while True:
            itemsUrl = self.url+"/site/searchpage.jsp?cp="+str(itemPageCount)+"&sp=%2Bcurrentprice%20skuidsaas&st="+urllib.parse.quote(self.itemToSearch)
            try:
                itemsPage = requests.get(itemsUrl, headers=self.headers)
            except requests.exceptions.RequestException as requestsException:
                print("Stopped trying to get pages for best buy at page "+str(itemPageCount))
                break

            searchedItemHtml = html.fromstring(itemsPage.content)

            try:
                itemList = itemList + searchedItemHtml.xpath(self.itemPageXpath+self.itemElementXpath)
            except Exception as e:
                print("Failed to find a list of items for best buy on page "+str(itemPageCount))
                print(e)
                break

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
            print("Failure on finding the BestBuy item PRICE!")
            print(e)


        itemLink = ""
        try:
            itemLink = self.url+str(itemElement.xpath(self.itemLinkXpath+"/@href")[0])
        except Exception as e:
            print("Failure on finding the BestBuy item LINK!")
            print(e)

        pictureHtmlLink = ""
        try:
            pictureHtmlLink = etree.tostring(itemElement.xpath(self.itemPictureXpath)[0], pretty_print=True).decode("utf-8")
        except Exception as e:
            print("Exception on finding the item bestbuy Picture Link!")
            print(e)

        itemName = ""
        try:
            itemName = itemElement.xpath(self.itemNameXpath)[0].text
        except Exception as e:
            print("Exception on finding the BestBuy item NAME")
            print(e)

        fullItem = WebsiteItem()
        fullItem.websiteName = "Best Buy"
        fullItem.itemPrice = itemPrice
        fullItem.itemName = itemName
        fullItem.itemPictureHtml = pictureHtmlLink
        if( len(itemLink) > 0 ):
            fullItem.itemLink = itemLink

        return fullItem

    def finish(self):
        self.myDriver.quit()