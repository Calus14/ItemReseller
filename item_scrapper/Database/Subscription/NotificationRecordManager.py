
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
            cur.execute("DELETE FROM notificationRecords WHERE subscription_id={}".format(subscriptionId))
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        self.databaseManager.databaseConnection.commit()
        cur.close()

    # Helper function for other managers to call
    def containsRecord(self, subscriptionId, itemLink):
        cur = self.databaseManager.databaseConnection.cursor()
        sqlString = "SELECT notificationRecords, itemLink FROM subscriptionHistoryRecords WHERE subscriptionId = '{}' AND itemLink = '{}'".format(subscriptionId, itemLink)

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

    # Called whenever we send out a email with a reference to the item for a given subscription
    def addRecord(self, record):
        cur = self.databaseManager.databaseConnection.cursor()
        insertCommand = """
                            INSERT INTO notificationRecords (recordId, subscriptionId, itemLink)
                            VALUES (%s, %s, %s)    
                        """

        try:
            cur.execute(insertCommand, (record.recordId, record.subscriptionId, record.itemLink))
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        self.databaseManager.databaseConnection.commit()
        cur.close()