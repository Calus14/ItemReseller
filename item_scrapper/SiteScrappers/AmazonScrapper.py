import re
import requests
from lxml import etree
from lxml import html
import urllib.parse
import json
from item_scrapper.SiteScrappers.WebsiteItem import WebsiteItem
from item_scrapper.SiteScrappers.WebsiteScrapper import WebsiteScrapper


class AmazonScrapper(WebsiteScrapper):


    url = "https://www.amazon.com/"
    headerMissingTraceId = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Dnt": "1",
        "Host": "httpbin.org",
        "Upgrade-Insecure-Requests": "1",
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    }

    searchedItemHtml = None

    itemPageXpath = "//div[@class='s-main-slot s-result-list s-search-results sg-row']"
    itemXpath = "//div[@data-index]"

    itemDollarHtml = '<span class="a-price-whole">'
    itemDecimalHtml= '<span class="a-price-decimal">'
    itemCentsHtml = '<span class="a-price-fraction">'

    itemLinkHtml = '<a class=".* a-link-normal .*" href='

    itemNameHtml = '<span class=".* a-text-normal" dir="auto">'

    itemPictureHtml = '<div class="a-section aok-relative s-image.*">'

    def initializeScrapper(self, itemToSearch):
        itemUrl = self.url+"s?k="+urllib.parse.quote(itemToSearch)

        #Refer to this post by Scrape Hero to understand why we need to fake out each call. In the future might also need to randomize to avoid bot detection
        #https://www.scrapehero.com/how-to-fake-and-rotate-user-agents-using-python-3/
        responseAsBytes = requests.get("http://httpbin.org/headers",headers=self.headerMissingTraceId).content
        headersAsString = responseAsBytes.decode("utf-8")
        headers = json.loads(headersAsString)['headers']


        itemsPage = requests.get(itemUrl, headers=headers)
        print(itemsPage.content.decode("utf-8"))
        self.searchedItemHtml = html.fromstring(itemsPage.content)


    def getPossibleItemWebElements(self):
        #Only look at the first page
        try:
            itemList = self.searchedItemHtml.xpath(self.itemPageXpath + self.itemXpath)
            print("Amazon list size")
            print(len(itemList))
            return itemList

        except Exception as e:
            print(e)


    def isValidWebElement(self, htmlElement):

        itemHtml = etree.tostring(htmlElement, pretty_print=True).decode("utf-8")

        if( not self.itemDollarHtml in itemHtml ):
            return False
        elif( not self.itemDecimalHtml in itemHtml ):
            return False
        elif( not re.search(self.itemNameHtml, itemHtml) ):
            return False

        return True

    def getItemFromWebElement(self, htmlElement):
        itemHtml = etree.tostring( htmlElement, pretty_print=True).decode("utf-8")

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
            # Amazon uses an internal reference link
            itemLink = "https://amazon.com"+itemHtml[linkStartIndex:linkEndIndex].replace('"', '')

        pictureHtmlLink = ""
        pictureMatch = re.search(self.itemPictureHtml, itemHtml)
        if( pictureMatch ):
            pictureStartIndex = pictureMatch.end(0)
            pictureEndIndex = pictureStartIndex + itemHtml[pictureStartIndex:].find(">")+1
            pictureHtmlLink = itemHtml[pictureStartIndex:pictureEndIndex].replace('\n', '')

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
