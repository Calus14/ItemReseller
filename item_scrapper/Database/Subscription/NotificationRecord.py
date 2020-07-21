from datetime import datetime, timedelta
import uuid

'''
A NotificationRecord Object is the history of the items that the user has been notified about for a given sub
This is a work around to storing variable length data (list<ItemRecord>) that was sent to the user. Allowing us to 
prevent sending them spam about the same item over and over and over again.
'''
class NotificationRecord:

    # Just a unique ID for the record of this historical event
    recordId = None
    # A Tie to the subsciption its a history for so we can purge this db when the sub expires
    subscriptionId = None
    # A Hash of the item itself that the user was notified about (initially just a hash of the link that is sent)
    itemHash = None

    def __init__(self, recordId, subscriptionId, itemHash):
        self.recordId = recordId
        self.subscriptionId = subscriptionId
        self.itemHash = itemHash

    def toJSON(self):
        return {"recordId" : self.recordId,
                "subscriptionId" : self.subscriptionId,
                "itemHash" : self.itemHash
                }

