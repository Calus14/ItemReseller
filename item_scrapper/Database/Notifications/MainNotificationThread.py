import concurrent.futures
import uuid

from item_scrapper import Application
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

    def __init__(self, rateToRunInSeconds = 30, maximumWorkers = 5):
        self.rateToRunInSeconds = rateToRunInSeconds
        self.maximumWorkers = maximumWorkers

    # Call this from the thread you create *start_new_thread*
    def runThread(self):
        # Gather all items that we need to check
        itemsToCheck = self.getAllMonitoredItems()

        threadExecutor = concurrent.futures.ThreadPoolExecutor(max_workers = self.maximumWorkers)
        notificationFutures = []
        for item in itemsToCheck:
            notificationFutures.append( threadExecutor.submit(self.doSingleItemNotificationLogic(item)) )

    def doSingleItemNotificationLogic(self, item):
        #Get all items across all sites, A User may not have specified to search ebay but they will take it and be happy if it meets the criteria
        itemInstances = self.getAllInstancesOfItem(item)

        #Recalculate the average as items may have been added or subtracted
        item.averageItemPrice = self.calculateAverageOfItem(itemInstances)
        # Lets keep our knowledge of the average so other parts of the app can access it.
        Application.itemManager.updateItem(item.itemName, item.averageItemPrice)

        #Get all subscriptions that care about this item (at the start will just be one but in the future it could be a lot)
        relevantSubscriptions = self.getSubscriptionsInterestedInItem(item)

        #Iterate over each subscription and do notifications on it based of the given items
        for sub in relevantSubscriptions:
            self.doNotificationsForSubscription(sub, itemInstances, item.averageItemPrice, item.itemName)

    def getAllMonitoredItems(self):
        print("Getting all monitored items")

        itemObjects = Application.itemManager.getAllItems()
        return itemObjects

    def getAllInstancesOfItem(self, item):
        print("Getting all instances of item "+item.itemName)

        allWebsites = list(Application.possibleWebsitesToSearch)
        allItemInstances = Application.findItemsHelper(allWebsites, item.itemName)

        return allItemInstances

    #TODO we need to take into account the "Relevance rating" of each item
    # the items are not sorted so they are in ranking of highest to lowest relevance for each site
    def calculateAverageOfItem(self, itemInstances):
        print("calculating average of each item")
        totalValue = 0
        for item in itemInstances:
            totalValue = totalValue+item.itemPrice
        return (totalValue/len(itemInstances))

    def getSubscriptionsInterestedInItem(self, item):
        print("Getting subs that care about "+ item.itemName)
        subsMonitoringItem = Application.subscriptionManager.getSubscriptions(item.itemName)
        return subsMonitoringItem

    def itemInstanceHasBeenNotifiedAbout(self, subscription, itemInstance):
        try:
            exists = Application.notificationsRecsManager.containsRecord(subscription.subscriptionId, hash(itemInstance.itemLink))
            print(" Turns out that this item instance with "+itemInstance.itemName+" has a value of :")
            print(exists)
            return exists
        except Exception as e:
            print(e)
            return False


    def doNotificationsForSubscription(self, subscription, itemInstances, avgPrice, itemName):

        itemsToNotifyAbout = []

        for itemInstance in itemInstances:

            if subscription.priceType == "Dollar":
                if(itemInstance.itemPrice <= subscription.pricePoint):
                    itemsToNotifyAbout.append(itemInstance)


            elif subscription.priceType == "Percent":
                itemPriceVsMarket = (itemInstance.itemPrice / avgPrice) * 100
                if(itemPriceVsMarket <= subscription.pricePoint):
                    itemsToNotifyAbout.append(itemInstance)

        #If we already notified the user about this item dont repeat it... they would be spammed with emails or texts or w/e
        filter(self.itemInstanceHasBeenNotifiedAbout, itemsToNotifyAbout)

        #We tie subs to uuid's not emails cause the user might delete their account and then the email is free again etc.
        user = Application.userManager.getUser(subscription.userId)

        #Email Notification
        Application.emailBroker.sendEmail(itemsToNotifyAbout, user.email, itemName)

        #Future notifications like Text etc.

        #Make a record to show that we notified about it already
        for itemInstance in itemInstances:
            notificationRecord = NotificationRecord(uuid.uuid4(), subscription.subscriptionId, hash(itemInstance.itemLink))
            Application.notificationsRecsManager.addRecord(notificationRecord)