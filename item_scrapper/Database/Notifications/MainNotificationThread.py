import concurrent.futures
import uuid
import time

from item_scrapper import FlaskApplication
from item_scrapper.Database.Subscription.NotificationRecord import NotificationRecord

'''
The Notifcation thread the class that looks over the item's data base and subscribtions database
perfoming periodic actions forever as long as the thread exists such as checking if a new item meets criteria to send
at notification. Running multiple of these threads is not a good idea
'''

class MainNotificationThread:

    # How often does it go and do its thing, defaults to 5 mins
    rateToRunInSeconds = 300
    # Number of workers/threads that will process the items
    # If there are 100 items that we are monitoring and we will run processing on each item then we can have N number of threads
    # each processing 1 item at a time
    maximumWorkers = 5

    #Kill switch for the thread
    shouldRun = True

    def __init__(self, rateToRunInSeconds = 1000, maximumWorkers = 5):
        self.rateToRunInSeconds = rateToRunInSeconds
        self.maximumWorkers = maximumWorkers

    # Call this from the thread you create *start_new_thread*
    def runThread(self):
        while( self.shouldRun ):

            # Gather all items that we need to check
            itemsToCheck = self.getAllMonitoredItems()

            threadExecutor = concurrent.futures.ThreadPoolExecutor(max_workers = self.maximumWorkers)
            testHolder = []

            for item in itemsToCheck:
                testHolder.append(threadExecutor.submit(self.doSingleItemNotificationLogic, item))

            time.sleep(self.rateToRunInSeconds)


    def doDummyMethod(self, number):
        print("Doing dummy on number "+str(number))

    def doSingleItemNotificationLogic(self, item):
        #Get all items across all sites, A User may not have specified to search ebay but they will take it and be happy if it meets the criteria
        itemInstances = self.getAllInstancesOfItem(item)

        #Recalculate the average as items may have been added or subtracted
        item.averageItemPrice = self.calculateAverageOfItem(itemInstances)
        # Lets keep our knowledge of the average so other parts of the app can access it.
        FlaskApplication.itemManager.updateItem(item.itemName, item.averageItemPrice)

        #Get all subscriptions that care about this item (at the start will just be one but in the future it could be a lot)
        relevantSubscriptions = self.getSubscriptionsInterestedInItem(item)

        #Iterate over each subscription and do notifications on it based of the given items
        for sub in relevantSubscriptions:
            self.checkForExpiredSub(sub)
            self.doNotificationsForSubscription(sub, itemInstances, item.averageItemPrice, item.itemName)

    def getAllMonitoredItems(self):
        print("Getting all monitored items")

        itemObjects = FlaskApplication.itemManager.getAllItems()
        return itemObjects

    def getAllInstancesOfItem(self, item):
        print("Getting all instances of item "+item.itemName)

        allWebsites = list(FlaskApplication.possibleWebsitesToSearch)
        allItemInstances = FlaskApplication.findItemsHelper(allWebsites, item.itemName)

        return allItemInstances

    #TODO we need to take into account the "Relevance rating" of each item
    # the items are not sorted so they are in ranking of highest to lowest relevance for each site
    def calculateAverageOfItem(self, itemInstances):
        print("calculating average of each item")
        itemInstances = sorted(itemInstances, key=lambda item: item.itemPrice)
        totalValue = 0
        for item in itemInstances:
            totalValue = totalValue+item.itemPrice
        return (totalValue/len(itemInstances))

    def getSubscriptionsInterestedInItem(self, item):
        print("Getting subs that care about "+ item.itemName)
        subsMonitoringItem = FlaskApplication.subscriptionManager.getSubscriptionsForItem(item.itemName)
        return subsMonitoringItem

    #def checkForExpiredSub(self, sub):
     #   if

    def itemInstanceHasBeenNotifiedAbout(self, subscription, itemInstance):
        try:
            exists = FlaskApplication.notificationsRecsManager.containsRecord(subscription.subscriptionId, itemInstance)
            return exists
        except Exception as e:
            print(e)
            #Something went wrong so we default to saying that the record exists so we dont naively send multiple notifications
            return True


    def doNotificationsForSubscription(self, subscription, itemInstances, avgPrice, itemName):

        itemsToNotifyAbout = []

        for itemInstance in itemInstances:
            if subscription.priceType == "Dollar":
                if(itemInstance.itemPrice <= float(subscription.pricePoint) and
                        not self.itemInstanceHasBeenNotifiedAbout(subscription, itemInstance)):
                    itemsToNotifyAbout.append(itemInstance)


            elif subscription.priceType == "Percent":
                itemPriceVsMarket = (itemInstance.itemPrice / avgPrice) * 100.0
                if(itemPriceVsMarket <= float(subscription.pricePoint) and
                        not self.itemInstanceHasBeenNotifiedAbout(subscription, itemInstance)):
                    itemsToNotifyAbout.append(itemInstance)

        #If we already notified the user about this item dont repeat it... they would be spammed with emails or texts or w/e
        #If there is no new items to report then were done
        if( len(itemsToNotifyAbout) == 0 ):
            return

        #We tie subs to uuid's not emails cause the user might delete their account and then the email is free again etc.
        user = FlaskApplication.userManager.getUser(subscription.userId)

        print("Sending "+str(len(itemsToNotifyAbout))+" items in the email")

        #Email Notification
        FlaskApplication.emailBroker.sendEmail(itemsToNotifyAbout, user.email, itemName)

        #Future notifications like Text etc.

        #Make a record to show that we notified about it already
        for item in itemsToNotifyAbout:
            notificationRecord = NotificationRecord(uuid.uuid4(), subscription.subscriptionId, item)
            FlaskApplication.notificationsRecsManager.addRecord(notificationRecord)