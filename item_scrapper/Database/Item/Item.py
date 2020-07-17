
import json

class Item:

    itemName: None
    averageItemPrice: None

    def __init__(self, itemName):
        self.itemName = itemName

    def toJSON(self):
        return json.dumps(self.__dict__)