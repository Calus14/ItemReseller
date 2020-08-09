

'''
Simple CRUD Wrapper for subscriptions that will be called via api's exposed to the front end. Some api's will be called
by internal logic and not the front end
'''
from item_scrapper.Database.Subscription.Subscription import Subscription
from item_scrapper import FlaskApplication


class SubscriptionManager:

    databaseManager = None

    def __init__(self, databaseManager):
        self.databaseManager = databaseManager
        print("Init Subscription Manager")

    # Called when expiration or the user asks to delete the subscription
    def deleteSubscription(self, subscriptionId, itemName):
        cur = self.databaseManager.databaseConnection.cursor()
        try:
            cur.execute("DELETE FROM subscriptions WHERE subscription_id='{}'".format(subscriptionId))
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        #After deleting any subscription we also need to delete all records that are associated with it.
        try:
            FlaskApplication.notificationsRecsManager.deleteRecordsBySubscription(subscriptionId)
        except Exception as e:
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        #Actually delete on the db
        self.databaseManager.databaseConnection.commit()

        #Now if there are 0 more subscriptions associated with the item itself. the item will need to be removed
        try:
            cur.execute("SELECT 1 FROM subscriptions WHERE item_name='{}'".format(itemName))
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        if cur.fetchone() is None:
            try:
                #The item no longer needs to be tracked
                FlaskApplication.itemManager.deleteItem(itemName)
            except Exception as e:
                raise e

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

        cur = self.databaseManager.databaseConnection.cursor()
        insertCommand =  """
                            INSERT INTO subscriptions (subscription_id, user_id, item_name, price_point, price_type, creation_time, expiration_time)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)    
                        """

        try:
            cur.execute(insertCommand, (subscription.subscriptionId, subscription.userId, subscription.itemName, str(subscription.pricePoint), subscription.priceType, subscription.creationTime, subscription.expirationTime))
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

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

        try:
            cur.execute(updateCommand, (str(subscription.pricePoint), subscription.priceType, subscription.subscriptionId))
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        self.databaseManager.databaseConnection.commit()
        cur.close()

    def getSubscriptionsForUser(self, userUUID):
        cur = self.databaseManager.databaseConnection.cursor()

        getByUserCommand = "SELECT * FROM subscriptions WHERE user_id='{}'".format(str(userUUID))
        try:
            cur.execute(getByUserCommand)
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        subsDbObjects = cur.fetchall()
        subs = []
        for dbObject in subsDbObjects:
            subscription = Subscription(dbObject[1], dbObject[2], dbObject[3], dbObject[4], 0)
            subscription.subscriptionId = dbObject[0]
            subs.append(subscription)

        self.databaseManager.databaseConnection.commit()
        cur.close()
        return subs

    # Used internally to query see if any subscription meets an item found on the internet
    def getSubscriptionsForItem(self, itemName):
        cur = self.databaseManager.databaseConnection.cursor()

        getByItemCommand = "SELECT * from subscriptions WHERE item_name='{}'".format(itemName)
        try:
            cur.execute(getByItemCommand)
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        subscriptionsForItem = cur.fetchall()
        subscriptions = []
        # Transform from the raw sql data to the object
        for sub in subscriptionsForItem:
            #TODO calculate teh actual hours to live
            subObject = Subscription(sub[1], sub[2], sub[3], sub[4], 0)
            subObject.subscriptionId = sub[0]
            subscriptions.append(subObject)

        self.databaseManager.databaseConnection.commit()
        cur.close()
        return subscriptions
