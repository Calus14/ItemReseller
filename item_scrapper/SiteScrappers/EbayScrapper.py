import re
import requests
from lxml import etree
from lxml import html
import urllib.parse
from item_scrapper.SiteScrappers.WebsiteItem import WebsiteItem
from item_scrapper.SiteScrappers.WebsiteScrapper import WebsiteScrapper


class EbayWebScrapper(WebsiteScrapper):

    url = "https://www.ebay.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    }
    searchedItemHtml = None

    itemPageXpath = "//ul[@class]"
    itemElementXpath = "//li[@class='s-item    '][@data-view]"
    itemElementXpathAlternative = "//li[@class='s-item    s-item--watch-at-corner'][@data-view]"

    itemPriceHtml = '<span class="s-item__price">'
    italicPriceHtml = '<span class="ITALIC">'

    itemNameHtml = '<h3 class="s-item__title">'

    itemLinkHtml = '<a .* class="s-item__link" href='
    itemPictureHtml = '<div class="s-item__image-helper"/>'

    maxRetries = 3

    def initializeScrapper(self, itemToSearch):
        itemUrl = self.url+"sch/i.html?_nkw="+urllib.parse.quote(itemToSearch)
        itemsPage = requests.get(itemUrl, headers=self.headers)
        self.searchedItemHtml = html.fromstring(itemsPage.content)

    def getPossibleItemWebElements(self):
        #Only look at the first page
        try:
            itemList = self.searchedItemHtml.xpath(self.itemPageXpath+self.itemElementXpath)
            itemList = itemList + self.searchedItemHtml.xpath(self.itemPageXpath+self.itemElementXpathAlternative)
            return itemList

        except Exception as e:
            print(e)

    def isValidWebElement(self, htmlElement):
        itemHtml = etree.tostring(htmlElement, pretty_print=True).decode("utf-8")

        if( not self.itemPriceHtml in itemHtml ):
            return False
        if( not self.itemNameHtml in itemHtml ):
            return False
        if(  not self.itemPictureHtml in itemHtml ):
            return False

        return True

    def getItemFromWebElement(self, htmlElement):
        itemHtml = etree.tostring( htmlElement, pretty_print=True).decode("utf-8")

        priceStartIndex = itemHtml.find(self.itemPriceHtml) + len(self.itemPriceHtml)
        priceEndIndex = priceStartIndex + itemHtml[priceStartIndex:].find("</span>")
        itemPrice = None
        try:
            itemPrice = float( itemHtml[priceStartIndex:priceEndIndex].replace(',', '').replace('$', '') )
        except Exception as e:
            # on Ebay there is a possibility of <low> to <high>
            try:
                priceEndIndex = priceStartIndex + itemHtml[priceStartIndex:].find("<span class")
                itemPrice = float( itemHtml[priceStartIndex:priceEndIndex].replace(',', '').replace('$', '') )
            except Exception as e2:
                # Finally there is also an option of it being italicized for some reason
                priceStartIndex = itemHtml.find(self.italicPriceHtml) + len(self.italicPriceHtml)
                priceEndIndex = priceStartIndex + itemHtml[priceStartIndex:].find("</span>")
                try:
                    itemPrice = float( itemHtml[priceStartIndex:priceEndIndex].replace(',', '').replace('$', '') )
                except:
                    print("price fail html is: "+itemHtml)

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


