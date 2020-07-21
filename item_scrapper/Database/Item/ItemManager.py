
'''
Simple CRUD Wrapper for Items that will be called via api's exposed to the front end. Some api's will be called
by internal logic and not the front end
'''
from item_scrapper.Database.Item.Item import Item


class ItemManager:

    databaseManager = None

    def __init__(self, databaseManager):
        self.databaseManager = databaseManager
        print("Init Item Manager")

    # If there are no more active subscriptions search for this item this will need to be called
    def deleteItem(self, itemName):
        cur = self.databaseManager.databaseConnection.cursor()
        try:
            cur.execute("DELETE FROM items WHERE item_name={}".format(itemName))
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        self.databaseManager.databaseConnection.commit()
        cur.close()

    # Helper function for other managers to call
    def containsItem(self, itemName):
        cur = self.databaseManager.databaseConnection.cursor()
        sqlString = "SELECT item_name FROM items WHERE item_name = '{}'".format(itemName)

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
    # Note the average price is usually calculated whenever we scan the internet to see if subscriptions should notify
    def addItem(self, itemName, averagePrice=0):
        cur = self.databaseManager.databaseConnection.cursor()
        insertCommand = """
                            INSERT INTO items (item_name, average_item_price)
                            VALUES (%s, %s)    
                        """

        try:
            cur.execute(insertCommand, (itemName, averagePrice))
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        self.databaseManager.databaseConnection.commit()
        cur.close()

    def updateItem(self, itemName, averagePrice):
        cur = self.databaseManager.databaseConnection.cursor()
        updateCommand = "UPDATE items SET average_item_price = {} where item_name = '{}'".format(averagePrice, itemName)

        try:
            cur.execute(updateCommand)
        except Exception as e:
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        self.databaseManager.databaseConnection.commit()
        cur.close()

    def getItem(self, itemName):
        cur = self.databaseManager.databaseConnection.cursor()
        getCommand = "SELECT * FROM items WHERE item_name={}".format(itemName)
        try:
            cur.execute(getCommand)
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        item = cur.fetchone()
        itemObject = Item(item[0], item[1])

        self.databaseManager.databaseConnection.commit()
        cur.close()
        return itemObject

    def getAllItems(self):
        cur = self.databaseManager.databaseConnection.cursor()
        getCommand = "SELECT * FROM items"
        try:
            cur.execute(getCommand)
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.rollback()
            cur.close()
            raise(e)

        items = cur.fetchall()
        itemObjects = []
        for item in items:
            itemObjects.append( Item(item[0], item[1]) )

        self.databaseManager.databaseConnection.commit()
        cur.close()
        return itemObjects
