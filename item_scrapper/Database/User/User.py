from datetime import datetime, timedelta
import json

class User:

    uniqueId = None
    email = None
    password = None
    dateCreated = None

    def __init__(self, password, email):
        self.password = password
        self.email = email

    def toJSON(self):
        def toJSON(self):
            return {"uniqueId" : self.uniqueId,
                    "email" : self.email,
                    "password" : self.password,
                    "dateCreated" : self.dateCreated,
                    }