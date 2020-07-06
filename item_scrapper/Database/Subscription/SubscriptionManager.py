

'''
Simple CRUD Wrapper for subscriptions that will be called via api's exposed to the front end. Some api's will be called
by internal logic and not the front end
'''
from item_scrapper.Database.DatabaseManager import DatabaseManager


class SubscriptionManager:

    databaseManager = None

    def __init__(self, databaseManager):
        self.databaseManager = databaseManager
        print("Init Subscription Manager")

    # Called when expiration or the user asks to delete the subscription
    def deleteSubscription(self, subscriptionId):
        cur = self.databaseManager.databaseConnection.cursor()
        cur.execute("DELETE FROM subscriptions WHERE subscription_id={}".format(subscriptionId))
        self.databaseManager.databaseConnection.commit()
        cur.close()

    # Helper function for other managers to call
    def containsSubscription(self, userId, item):
        cur = self.databaseManager.databaseConnection.cursor()
        sqlString = "SELECT user_id, item_name FROM subscriptions WHERE user_id = '{}' AND item_name = '{}'".format(userId, item)

        try:
            cur.execute(sqlString)
        except Exception as e:
            print(e)
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            return False

        doesExist = cur.fetchone() is not None
        self.databaseManager.databaseConnection.commit()
        cur.close()
        return doesExist

    # Called by front end to add a new subscription
    def addSubscription(self, subscription):
        #TODO Upon adding a subscription add a new item and fire off an event to find its average price if it is a new item

        if( self.containsSubscription(subscription.userId, subscription.itemName) ):
            raise Exception ("A Subscription for the item {} already exists for this user".format(subscription.itemName) )

        cur = self.databaseManager.databaseConnection.cursor()
        insertCommand =  """
                            INSERT INTO subscriptions (subscription_id, user_id, item_name, price_point, price_type, creation_time, expiration_time)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)    
                        """

        cur.execute(insertCommand, (subscription.subscriptionId, subscription.userId, subscription.itemName, str(subscription.pricePoint), subscription.priceType, subscription.creationTime, subscription.expirationTime))
        self.databaseManager.databaseConnection.commit()
        cur.close()

    # If the user wants to extend/change the subscription
    def updateSubscription(self, subscription):
        if( not self.containsSubscription(subscription.userId, subscription.itemName) ):
            raise Exception ("A Subscription for the item %s must already exists for this user to update it", subscription.itemName)

        cur = self.databaseManager.databaseConnection.cursor()
        updateCommand =  """
                            UPDATE subscriptions
                            SET price_point = %s, price_type = %s
                            WHERE subscription_id = %s     
                        """

        cur.execute(updateCommand, (str(subscription.pricePoint), subscription.priceType, subscription.subscriptionId))
        self.databaseManager.databaseConnection.commit()
        cur.close()

    # Used internally to query see if any subscription meets an item found on the internet
    def getSubscriptions(self, itemName):
        cur = self.databaseManager.databaseConnection.cursor()

        getByItemCommand = "SELECT * from subscriptions WHERE item_name='{}'".format(itemName)
        cur.execute(getByItemCommand, (itemName))
        subscriptionsForItem = cur.fetchall()
        self.databaseManager.databaseConnection.commit()
        cur.close()
        return subscriptionsForItem
