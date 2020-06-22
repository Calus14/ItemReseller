from item_scrapper.SiteScrappers import EbayScrapper, AmazonScrapper
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

@app.route('/listOfItems/', methods=['POST'])
@cross_origin()
def findListOfItemsOrdered():
    thing = request
    print(request.json)
    searchItem = request.json["searchItem"]
    websitesToSearch = request.json["websitesToSearch"]

    scrapperFutures = []
    # keep these in scope so we can finish them
    scrappers = []
    for website in websitesToSearch:
        if website not in possibleWebsitesToSearch:
            print("Error! Was sent a website named "+website+" but no scrapper exists for it.")
            continue;

        singleExecutor = concurrent.futures.ThreadPoolExecutor(max_workers = 1)
        websiteScrapper = copy.deepcopy(possibleWebsitesToSearch[website])
        scrappers.append(websiteScrapper)
        scrapperFutures.append( singleExecutor.submit(websiteScrapper.scrapeWebsite, searchItem) )

    websiteItems = []
    for future in scrapperFutures:
        websiteItems.extend(future.result())

    for scrapper in scrappers:
        scrapper.finish()

    sortedItems = sorted(websiteItems, key=lambda item: item.itemPrice)

    returnList = []
    for item in sortedItems:
        returnList.append( {"Name": item.itemName, "Price": "$"+str(item.itemPrice), "Link": item.itemLink, "Website": item.websiteName })

    jsonHelper = {"sortedItems":returnList}
    return jsonify(jsonHelper)