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
    "Amazon" : AmazonScrapper.AmazonScrapper(),
    "Ebay" : EbayScrapper.EbayWebScrapper(),
}

@app.route('/listOfItems', methods=['POST'])
@cross_origin()
def findListOfItemsOrdered():
    searchItem = request.json["searchItem"]
    websitesToSearch = request.json["websitesToSearch"]

#TODO look at this post as it might be the solution for allowing threading of the chrome driver
#https://medium.com/@mikelcbrowne/running-chromedriver-with-python-selenium-on-heroku-acc1566d161c
    scrapperFutures = []
    # keep these in scope so we can finish them
    scrappers = []
    threadExecutor = concurrent.futures.ThreadPoolExecutor(max_workers = len(websitesToSearch) * 2 )
    for website in websitesToSearch:
        if website not in possibleWebsitesToSearch:
            print("Error! Was sent a website named "+website+" but no scrapper exists for it.")
            continue;

        websiteScrapper = copy.deepcopy(possibleWebsitesToSearch[website])
        scrappers.append(websiteScrapper)
        #scrapperFutures.append( threadExecutor.submit(websiteScrapper.scrapeWebsite, searchItem) )

    websiteItems = []
    #for future in scrapperFutures:
        #websiteItems.extend(future.result())

    for scrapper in scrappers:
        websiteItems.extend(scrapper.scrapeWebsite(searchItem))

    for scrapper in scrappers:
        scrapper.finish()

    sortedItems = sorted(websiteItems, key=lambda item: item.itemPrice)

    returnList = []
    for item in sortedItems:
        returnList.append( {"Name": item.itemName, "Price": "$"+str(item.itemPrice), "Image": item.itemPictureHtml, "Link": item.itemLink, "Website": item.websiteName })

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
