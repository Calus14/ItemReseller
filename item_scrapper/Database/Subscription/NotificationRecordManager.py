
'''
Simple CRUD Wrapper for notificationRecords that will be called via api's exposed to the front end. Some api's will be called
by internal logic and not the front end
'''

class NotificationRecordManager:

    databaseManager = None

    def __init__(self, databaseManager):
        self.databaseManager = databaseManager
        print("Init Notification Record Manager")

    # Whenever a subscribtion is deleted or expires, all records attached too it will need to be removed
    def deleteRecordsBySubscription(self, subscriptionId):
        cur = self.databaseManager.databaseConnection.cursor()
        try:
            cur.execute("DELETE FROM notificationRecords WHERE subscriptionId={}".format(subscriptionId))
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        self.databaseManager.databaseConnection.commit()
        cur.close()

    # Helper function for other managers to call
    def containsRecord(self, subscriptionId, websiteItem):
        cur = self.databaseManager.databaseConnection.cursor()
        sqlString = "SELECT subscriptionId, itemName, itemPrice, itemWebsite FROM notificationRecords " \
                    "WHERE subscriptionId = '{}' AND itemName = '{}' AND itemPrice = {} AND itemWebsite='{}'".format(subscriptionId, websiteItem.itemName, str(websiteItem.itemPrice), websiteItem.websiteName)

        try:
            cur.execute(sqlString)
        except Exception as e:
            print(e)
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            return False

        item = cur.fetchone()
        doesExist = item is not None
        self.databaseManager.databaseConnection.commit()
        cur.close()
        return doesExist

    # Called whenever we send out a email with a reference to the item for a given subscription
    def addRecord(self, record):
        cur = self.databaseManager.databaseConnection.cursor()

        insertCommand = """
                            INSERT INTO notificationRecords (recordId, subscriptionId, itemName, itemPrice, itemLink, itemImageLink, itemWebsite)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)    
                        """

        try:
            cur.execute(insertCommand, (record.recordId, record.subscriptionId, record.websiteItem.itemName, record.websiteItem.itemPrice, record.websiteItem.itemLink, record.websiteItem.itemPictureHtml, record.websiteItem.websiteName))
        except Exception as e:
            print (e)
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        self.databaseManager.databaseConnection.commit()
        cur.close()

    def getSubscriptionNotificationRecords(self, subscriptionId):
        cur = self.databaseManager.databaseConnection.cursor()
        getCommand = "SELECT * FROM notificationRecords WHERE subscriptionId = '{}'".format(subscriptionId)

        try:
            cur.execute(getCommand)
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        recordDbObjects = cur.fetchall()
        recordedItems = []
        for dbObject in recordDbObjects:
            recordedItems.append({ 'itemName': dbObject[2],
                                    'itemImg': dbObject[5],
                                  'itemLink': dbObject[4],
                                  'itemPrice': str(dbObject[3])})

        self.databaseManager.databaseConnection.commit()
        cur.close()

        return recordedItems

