
import requests
from lxml import etree
from lxml import html
import urllib.parse
from item_scrapper.SiteScrappers.WebsiteItem import WebsiteItem
from item_scrapper.SiteScrappers.WebsiteScrapper import WebsiteScrapper

class WalmartScrapper(WebsiteScrapper):


    url = "https://www.walmart.com/"
    maximumPagesToGrab = 5
    itemToSearch = ''

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    }

    itemPageGridXpath = "//ul[@data-automation-id='search-result-gridview-items']"
    itemElementGridXpath = "//li[@data-tl-id]"

    itemPageListXpath = "//div[@data-automation-id='search-result-listview-items']"
    itemElementListXpath = "//div[@data-tl-id]"

    itemPriceXpath = './/span[@class="price-main-block"]//span[@class="visuallyhidden"]'

    itemNameXpath = './/div[contains(@class, "search-result-product-title")]/span[@class="visuallyhidden"]'

    itemLinkXpath = './/a[contains(@class, "product-title-link")]'

    itemPictureXpath = './/div[@class="orientation-square"]/img'

    maxRetries = 3

    def initializeScrapper(self, itemToSearch):
        self.itemToSearch = itemToSearch

    def getPossibleItemWebElements(self):
        itemList = []
        itemPageCount = 1
        itemsCount = 0

        while True:
            itemUrl = self.url+"/search/?page="+str(itemPageCount)+"&&ps="+str(itemsCount)+"&query="+urllib.parse.quote(self.itemToSearch)
            try:
                itemsPage = requests.get(itemUrl, headers=self.headers)
            except requests.exceptions.RequestException as requestsException:
                print("Stopped trying to get pages for Walmart at page "+str(itemPageCount))
                break

            searchedItemHtml = html.fromstring(itemsPage.content)

            try:
                # Adding them together because if one fails it just returns an empty list this
                itemList = itemList + searchedItemHtml.xpath(self.itemPageGridXpath+self.itemElementGridXpath)
                itemList = itemList + searchedItemHtml.xpath(self.itemPageListXpath+self.itemElementListXpath)
            except Exception as e:
                print("Failed to find a list of items for Walmart on page"+str(itemPageCount))
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
            print("Failure on finding the walmart item PRICE!")
            print(e)


        itemLink = ""
        try:
            itemLink = "https://walmart.com/"+str(itemElement.xpath(self.itemLinkXpath+"/@href")[0])
        except Exception as e:
            print("Failure on finding the walmart item LINK!")
            print(e)

        pictureHtmlLink = ""
        try:
            pictureHtmlLink = etree.tostring(itemElement.xpath(self.itemPictureXpath)[0], pretty_print=True).decode("utf-8")
        except Exception as e:
            print("Exception on finding the item Picture Link!")
            print(e)

        itemName = ""
        try:
            itemName = itemElement.xpath(self.itemNameXpath)[0].text
        except Exception as e:
            print("Exception on finding the item NAME")
            print(e)

        fullItem = WebsiteItem()
        fullItem.websiteName = "Walmart"
        fullItem.itemPrice = itemPrice
        fullItem.itemName = itemName
        fullItem.itemPictureHtml = pictureHtmlLink
        if( len(itemLink) > 0 ):
            fullItem.itemLink = itemLink

        return fullItem

    def finish(self):
        self.myDriver.quit()