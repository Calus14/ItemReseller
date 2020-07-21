
import json

class Item:

    itemName: None
    averageItemPrice: None

    def __init__(self, itemName, averageItemPrice = 0):
        self.itemName = itemName
        self.averageItemPrice = averageItemPrice

    def toJSON(self):
        return json.dumps(self.__dict__)