from abc import ABC, abstractmethod

class WebsiteScrapper(ABC):

    #First initializer will call the web driver to intialize selenium (This is to account for future sites that use JS to load their html)

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