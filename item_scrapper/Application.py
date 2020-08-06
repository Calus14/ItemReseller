
from item_scrapper.Database.Item.ItemManager import ItemManager
from item_scrapper.Database.Notifications.EmailBroker import EmailBroker
from item_scrapper.Database.Notifications.MainNotificationThread import MainNotificationThread
from item_scrapper.Database.User.User import User
from item_scrapper.Database.User.UserManager import UserManager
from item_scrapper.SiteScrappers import EbayScrapper, AmazonScrapper
import concurrent.futures
import _thread
import copy
import uuid
from datetime import datetime
from flask import Flask, jsonify, request, abort, Response
from flask_cors import CORS, cross_origin

from item_scrapper.Database.DatabaseManager import DatabaseManager
from item_scrapper.Database.Subscription.SubscriptionManager import SubscriptionManager
from item_scrapper.Database.Subscription.NotificationRecordManager import NotificationRecordManager
from item_scrapper.Database.Subscription.Subscription import Subscription


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

possibleWebsitesToSearch = {
    "amazon" : AmazonScrapper.AmazonScrapper(),
    "ebay" : EbayScrapper.EbayWebScrapper(),
}

'''
Managers for databases, emails, etc. If this ever grows large each is intended to be its own micro service
'''
dbManager = DatabaseManager()
dbManager.createTablesIfNeeded()

emailBroker = EmailBroker(app)

subscriptionManager = SubscriptionManager(databaseManager=dbManager)
itemManager = ItemManager(databaseManager=dbManager)
userManager = UserManager(databaseManager=dbManager)
notificationsRecsManager = NotificationRecordManager(databaseManager=dbManager)

notificationContinuousThread = MainNotificationThread()

_thread.start_new_thread ( notificationContinuousThread.runThread, () )

# Helper function that can be called anywhere in the server
def findItemsHelper(websitesToSearch, searchItem):
    scrapperFutures = []
    threadExecutor = concurrent.futures.ThreadPoolExecutor(max_workers = len(websitesToSearch) )
    for website in websitesToSearch:
        if website not in possibleWebsitesToSearch:
            print("Error! Was sent a website named "+website+" but no scrapper exists for it.")
            continue;

        websiteScrapper = copy.deepcopy(possibleWebsitesToSearch[website])
        scrapperFutures.append( threadExecutor.submit(websiteScrapper.scrapeWebsite, searchItem) )

    websiteItems = []
    for future in scrapperFutures:
        websiteItems.extend(future.result())

    return websiteItems


'''
Because For now im using heroku as a free service the dyno's will go away after 30 minutes of inactivity
This route is a heartbeat message that will go out ever 5 minutes just so both the frontend app
and the webserver will stay running
'''
@app.route('/heartbeat', methods=['GET'])
def getHeartBeat():
    return "Can't Stop Staying Alive"

@app.route('/listOfItems', methods=['POST'])
@cross_origin()
def findListOfItemsOrdered():
    searchItem = request.json["searchItem"]
    websitesToSearch = request.json["websitesToSearch"]

    websiteItems = findItemsHelper(websitesToSearch, searchItem)

    sortedItems = sorted(websiteItems, key=lambda item: item.itemPrice)

    returnList = []
    for item in sortedItems:
        formattedPrice = "{:.2f}".format(item.itemPrice)
        returnList.append( {"Name": item.itemName, "Price": "$"+formattedPrice, "Image": item.itemPictureHtml, "Link": item.itemLink, "Website": item.websiteName })

    jsonHelper = {"sortedItems":returnList}

    return jsonify(jsonHelper)

'''
Tries to add a new subscribption object to the database. the user ID much match one in our user db and be unique on that user
'''
@app.route('/submitSubscription', methods=['POST'])
@cross_origin()
def addSubscription():
    newSub = Subscription(userId = request.json['userId'],
                          itemName = request.json['itemName'],
                          pricePoint = request.json['pricePoint'],
                          priceType = request.json['priceType'],
                          hoursToLive = int(request.json['hoursToLive']) )
    if "Dollar" in newSub.priceType:
        newSub.priceType = "Dollar"
    elif "Percent" in newSub.pricePoint:
        newSub.priceType = "Percent"
    try:
        subscriptionManager.addSubscription(subscription = newSub)
    except Exception as e:
        print(e)
        abort( 500, Response(str(e)) )

    # After adding a subscription we need to make a note that this item is now being watched
    try:
        if( itemManager.containsItem(newSub.itemName)==False ):
            itemManager.addItem(newSub.itemName)
    except Exception as e:
        print(e)
        abort( 500, Response(str(e)) )

    print("Added subscription now with id "+str(newSub.subscriptionId))
    return jsonify(newSub.toJSON())

'''
Finds all active subscriptions for a given user
'''
@app.route("/userSubscriptions", methods=['POST'])
@cross_origin()
def getUserSubscriptions():
    userId = request.json['userId']

    try:
        subscriptions = subscriptionManager.getSubscriptionsForUser(userId)
        answerJsonObjs = []
        for sub in subscriptions:
            answerJsonObjs.append(sub.toJSON())
        return jsonify(answerJsonObjs)

    except Exception as e:
        print(e)
        abort( 500, Response(str(e)) )

'''
Used to tell other services what specific listings have already been found and notified for a given subscription
'''
@app.route("/subscriptionItems", methods=['POST'])
@cross_origin()
def getNotifiedSubscriptionItems():
    subscriptionId = request.json['subscriptionId']

    try:
        notificationRecords = notificationsRecsManager.getSubscriptionNotificationRecords(subscriptionId)
        return jsonify(notificationRecords)

    except Exception as e:
        print(e)
        abort( 500, Response(str(e)) )

'''
USED to delete an active subscription from a users database
'''
@app.route("/userSubscriptions", methods=['DELETE'])
@cross_origin()
def deleteNotification():
    subscriptionId = request.json['subscriptionId']

    try:
        subscriptionManager.deleteSubscription(subscriptionId)
        return

    except Exception as e:
        print(e)
        abort( 500, Response(str(e)) )


'''
Checks to see if a user exists
'''
@app.route('/userExists', methods=['POST'])
@cross_origin()
def checkUserExistance():
    print("hit the User exsits")

    print(request.json)
    if userManager.containsUser(request.json['email']) :
        print("User Found to be contained")
        return "true"
    else:
        return "false"

''''
TODO Fix this to use vue authentication refering to https://blog.sqreen.com/authentication-best-practices-vue/
'''
@app.route('/loginUser', methods=['POST'])
@cross_origin()
def loginUser():
    try:
        userId = userManager.getUserId(request.json['email'], request.json['password'])
    except Exception as e:
        print("Invalid user login for email "+request.json['email'])
        abort( 404, Response(str(e)) )

    #Dont return the full object it has other info thats sensative.
    return jsonify( {"userUniqueId" : userId} )

'''
Tries to add a new user
'''
@app.route('/addUser', methods=['POST'])
@cross_origin()
def addUser():
    print("hit the add User")
    newUser = User(
                    uniqueId = uuid.uuid4(),
                    email = request.json['email'],
                    password = request.json['password'],
                    dateCreated = datetime.now())
    try:
        userManager.addUser(user = newUser)
    except Exception as e:
        print(e)
        abort( 500, Response(str(e)) )

    print("Added subscription now with id "+newUser.email)
    return jsonify( {"userUniqueId" : newUser.uniqueId} )
