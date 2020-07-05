from item_scrapper.SiteScrappers import EbayScrapper, AmazonScrapper
from item_scrapper import EmailManager
import concurrent.futures
import copy
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

possibleWebsitesToSearch = {
    "amazon" : AmazonScrapper.AmazonScrapper(),
    "ebay" : EbayScrapper.EbayWebScrapper(),
}

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

    scrapperFutures = []
    threadExecutor = concurrent.futures.ThreadPoolExecutor(max_workers = len(websitesToSearch) * 2 )
    for website in websitesToSearch:
        if website not in possibleWebsitesToSearch:
            print("Error! Was sent a website named "+website+" but no scrapper exists for it.")
            continue;

        websiteScrapper = copy.deepcopy(possibleWebsitesToSearch[website])
        scrapperFutures.append( threadExecutor.submit(websiteScrapper.scrapeWebsite, searchItem) )

    websiteItems = []
    for future in scrapperFutures:
        websiteItems.extend(future.result())

    sortedItems = sorted(websiteItems, key=lambda item: item.itemPrice)

    returnList = []
    for item in sortedItems:
        formattedPrice = "{:.2f}".format(item.itemPrice)
        returnList.append( {"Name": item.itemName, "Price": "$"+formattedPrice, "Image": item.itemPictureHtml, "Link": item.itemLink, "Website": item.websiteName })

    jsonHelper = {"sortedItems":returnList}

    return jsonify(jsonHelper)

'''
Will try to add a new Subscription object to the data base, if the email already exists will update the data on it.
'''
@app.route('/submitSubscription', methods=['POST'])
@cross_origin()
def addSubscription():
    print("hit the submit")
    return "This Worked"
