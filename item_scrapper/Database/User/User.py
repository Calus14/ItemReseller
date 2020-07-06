from datetime import datetime, timedelta

class User:

    uniqueId = None
    email = None
    password = None
    dateCreated = None

    def __init__(self, password, email):
        self.password = password
        self.email = email