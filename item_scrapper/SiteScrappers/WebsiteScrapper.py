import time
from abc import ABC, abstractmethod

class WebsiteScrapper(ABC):

    #First initializer will call the web driver to intialize selenium (This is to account for future sites that use JS to load their html)
    @abstractmethod
    def initializeScrapper(self, itemToSearch):
        pass

    #Method that upon entering Item Search and waiting 3 seconds (for the page to load) will get all webElements
    # that can possibly represent a valid Item
    @abstractmethod
    def getPossibleItemWebElements(self):
        pass

    #Simple test to see if the web element has the correct info/properties to be used to create a searchabale item
    @abstractmethod
    def isValidWebElement(self, htmlElement):
        pass

    # Takes a web element and builds a site Item Object
    @abstractmethod
    def getItemFromWebElement(self, htmlElement):
        pass

    def scrapeWebsite(self, itemToSearch):

        filledWebItems = []
        self.initializeScrapper(itemToSearch)

        possibleWebElements = self.getPossibleItemWebElements()

        for possibleElement in possibleWebElements:
            if( self.isValidWebElement(possibleElement)):
                filledWebItems.append(self.getItemFromWebElement(possibleElement))

        return filledWebItems