
import requests
from lxml import etree
from lxml import html
import urllib.parse
from item_scrapper.SiteScrappers.WebsiteItem import WebsiteItem
from item_scrapper.SiteScrappers.WebsiteScrapper import WebsiteScrapper

class NikeScrapper(WebsiteScrapper):

    url = "https://www.bestbuy.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    }
    searchedItemHtml = None

    itemPageGridXpath = "//ul[@data-automation-id='search-result-gridview-items']"

    itemPageListXpath = "//div[@data-automation-id='search-result-listview-items']"
    itemElementListXpath = "//div[@data-tl-id]"

    itemPriceXpath = ''
    itemNameXpath = ''
    itemLinkXpath = ''
    itemPictureXpath = ''

    maxRetries = 3

    def initializeScrapper(self, itemToSearch):
        itemUrl = self.url+"/search/?query="+urllib.parse.quote(itemToSearch)
        itemsPage = requests.get(itemUrl, headers=self.headers)
        self.searchedItemHtml = html.fromstring(itemsPage.content)

    def getPossibleItemWebElements(self):
        #Only look at the first page
        try:
            # Adding them together because if one fails it just returns an empty list this
            itemList = self.searchedItemHtml.xpath(self.itemPageGridXpath+self.itemElementGridXpath)
            return itemList

        except Exception as e:
            print(e)

    def isValidWebElement(self, itemElement):
        return False

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