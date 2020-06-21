import time
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class AmazonScrapper:

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

    maxRetries = 3

    def __init__(self):
        self.myDriver = webdriver.Chrome(ChromeDriverManager().install())
        self.myDriver.get(self.url)
        print("Initializted Amazon Scrapper")


    def priceSearch(self, searchItem):

        try:
            searchBox = self.myDriver.find_element_by_xpath(self.searchBoxXpath)
            searchBox.send_keys(searchItem)
            searchButton = self.myDriver.find_element_by_xpath(self.searchButtonXpath)
            searchButton.click()
        except NoSuchElementException as e:
            print(e)
            print("Failed to enter into the text box and press the button")
            return

        #Gaurentee that it loads the new page source correctly
        time.sleep(3)

        itemList = []
        itemDict = {}
        #Only look at the first page
        for tries in range(self.maxRetries):
            try:
                itemList = self.myDriver.find_elements_by_xpath(self.itemPageXpath+self.itemXpath)
                print("Amazon list size")
                print(len(itemList))
                break

            except Exception as e:
                print(e)
                time.sleep(1)


        for itemWebElement in itemList:
            itemHtml = itemWebElement.get_attribute("innerHTML")
            if( not self.itemDollarHtml in itemHtml or not self.itemDecimalHtml in itemHtml or not re.search(self.itemNameHtml, itemHtml) ):
                continue

            dollarStartIndex = itemHtml.find(self.itemDollarHtml) + len(self.itemDollarHtml)
            dollarEndIndex = itemHtml.find(self.itemDecimalHtml)

            dollarAmount = float( itemHtml[dollarStartIndex:dollarEndIndex].replace(',', '').replace('"', '') )

            centsStartIndex = itemHtml.find(self.itemCentsHtml) + len(self.itemCentsHtml)
            centsEndIndex = centsStartIndex + itemHtml[centsStartIndex:].find("</span>")
            centsAmount = float( itemHtml[centsStartIndex:centsEndIndex].replace('"', '') )

            itemLink = ""
            if( re.search(self.itemLinkHtml, itemHtml) ):
                matchObj = re.search(self.itemLinkHtml, itemHtml)
                linkStartIndex = matchObj.end(0)
                linkEndIndex = linkStartIndex + itemHtml[linkStartIndex:].find(">")
                itemLink = itemHtml[linkStartIndex:linkEndIndex].replace('"', '')

            nameMatch = re.search(self.itemNameHtml, itemHtml)
            nameStartIndex = nameMatch.end(0)
            nameEndIndex = nameStartIndex + itemHtml[nameStartIndex:].find("</span>")
            itemName = itemHtml[nameStartIndex:nameEndIndex]

            itemDict[itemName] = [dollarAmount+(centsAmount/100), itemLink]

        print("Ammazon")
        print( len(itemDict) )
        return itemDict


    def finish(self):
        self.myDriver.quit()