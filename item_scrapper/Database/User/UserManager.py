import uuid
from datetime import datetime, timedelta

from item_scrapper.Database.User.User import User

'''
Simple CRUD Wrapper for Users mainly it will be used to create or to login... on beta it will be a very rough draft
but in the future will start to use AWS and google to manage passwords etc.
'''

class UserManager:

    databaseManager = None

    def __init__(self, databaseManager):
        self.databaseManager = databaseManager
        print("Init User Manager")

    # Helper function for other managers to call
    def containsUser(self, email):
        cur = self.databaseManager.databaseConnection.cursor()
        sqlString = "SELECT user_email FROM users WHERE user_email='{}'".format( email)
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

    # Called by front end to add a new user
    def addUser(self, user):
        if( self.containsUser(user.email) ):
            raise Exception ("A user with email {} already exists cannot add them".format(user.email) )

        cur = self.databaseManager.databaseConnection.cursor()
        user.uniqueId = uuid.uuid4()
        user.dateCreated = datetime.now()
        insertCommand =  """
                            INSERT INTO users (user_id, user_email, user_password, creation_time)
                            VALUES (%s, %s, %s, %s)    
                        """

        try:
            cur.execute(insertCommand, (user.uniqueId, user.email, user.password, user.dateCreated))
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.commit()
            cur.close()
            raise(e)

        self.databaseManager.databaseConnection.commit()
        cur.close()

    # If the user wants to change anything about themselfs
    def updateUser(self, user):
        retrievedUser = self.getUserId( user.uniqueId )
        if( retrievedUser is None ):
            raise Exception ("A user with email %s was tried to update in the database but it does not apparently exist.", user.email)

        cur = self.databaseManager.databaseConnection.cursor()
        dateupdated = datetime.now()
        updateCommand =  """
                            UPDATE users
                            SET user_email = %s, user_password = %s, creation_time = %s
                            WHERE user_id = %s     
                        """
        try:
            cur.execute(updateCommand, (user.email, user.password, dateupdated, user.uniqueId) )
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.commit()
            cur.close()
            raise(e)
        self.databaseManager.databaseConnection.commit()
        cur.close()

    # TODO work on this when we actually care about security
    def getUserId(self, email, password):
        cur = self.databaseManager.databaseConnection.cursor()

        getByUUidCommand = "SELECT * from users WHERE user_email=%s AND user_password=%s"
        try:
            cur.execute(getByUUidCommand, (email, password))
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.commit()
            cur.close()
            raise(e)

        user = cur.fetchone()
        if user is None:
            raise( Exception("User was not able to be found"))

        userId = user[0]

        self.databaseManager.databaseConnection.commit()
        cur.close()
        return userId

    def getUser(self, userId):
        cur = self.databaseManager.databaseConnection.cursor()

        getByUUidCommand = "SELECT * from users WHERE user_id='{}'".format(userId)
        try:
            cur.execute(getByUUidCommand)
        except Exception as e:
            # if we dont close the conneection on a failed execute we wont will lock the process
            self.databaseManager.databaseConnection.commit()
            cur.close()
            raise(e)

        user = cur.fetchone()
        if user is None:
            raise( Exception("User was not able to be found"))

        userObj = User( user[0], user[1], user[2], user[3])

        self.databaseManager.databaseConnection.commit()
        cur.close()
        return userObj