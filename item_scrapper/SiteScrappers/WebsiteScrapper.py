import time
from abc import ABC, abstractmethod

class WebsiteScrapper(ABC):

    maxRetries = 3

    #First initializer will call the web driver to intialize selenium (This is to account for future sites that use JS to load their html)
    @abstractmethod
    def initializeScrapper(self):
        pass

    # Method that will interact with the main page in whatever way is needed in order to search correctly,
    # Allows for future functionality like selecting preferences
    @abstractmethod
    def enterItemSearch(self, itemToSearch):
        pass

    #Method that upon entering Item Search and waiting 3 seconds (for the page to load) will get all webElements
    # that can possibly represent a valid Item
    @abstractmethod
    def getPossibleItemWebElements(self):
        pass

    #Simple test to see if the web element has the correct info/properties to be used to create a searchabale item
    @abstractmethod
    def isValidWebElement(self, webElement):
        pass

    # Takes a web element and builds a site Item Object
    @abstractmethod
    def getItemFromWebElement(self, webElement):
        pass

    @abstractmethod
    def finish(self):
        pass

    def scrapeWebsite(self, itemToSearch):

        filledWebItems = []
        self.initializeScrapper()
        self.enterItemSearch(itemToSearch)
        #Because enterItemSearch doesnt block until the page has loaded we are using this hack
        # in the future we can probably check the driver to see if its loaded
        time.sleep(1)
        possibleWebElements = self.getPossibleItemWebElements()

        for possibleElement in possibleWebElements:
            if( self.isValidWebElement(possibleElement)):
                filledWebItems.append(self.getItemFromWebElement(possibleElement))

        return filledWebItems