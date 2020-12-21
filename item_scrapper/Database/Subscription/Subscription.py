from datetime import datetime, timedelta
import \
    uuid

class Subscription:

    subscriptionId = None
    userId = None
    itemName = None
    pricePoint = None
    priceType = "Dollar"

    creationTime = None
    expirationTime = None

    def __init__(self, userId, itemName, pricePoint, priceType, hoursToLive):
        self.subscriptionId = uuid.uuid4()
        self.userId = userId
        self.itemName = itemName
        self.pricePoint = pricePoint
        if(priceType is not None):
            self.priceType = priceType
        self.creationTime = datetime.now()
        #Assuming this is right
        self.expirationTime = self.creationTime + timedelta(hours= hoursToLive)

    def toJSON(self):
        return {"subscriptionId" : self.subscriptionId,
                "userId" : self.userId,
                "itemName" : self.itemName,
                "pricePoint" : str(self.pricePoint),
                "priceType" : self.priceType,
                "creationTime" : self.creationTime,
                "expirationTime" : self.expirationTime
                }

