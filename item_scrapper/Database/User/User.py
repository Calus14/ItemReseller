from datetime import datetime, timedelta
import json

class User:

    uniqueId = None
    email = None
    password = None
    dateCreated = None

    def __init__(self, uniqueId, email, password, dateCreated):
        self.uniqueId = uniqueId
        self.password = password
        self.email = email
        self.dateCreated = dateCreated

    def toJSON(self):
        def toJSON(self):
            return {"uniqueId" : self.uniqueId,
                    "email" : self.email,
                    "password" : self.password,
                    "dateCreated" : self.dateCreated,
                    }