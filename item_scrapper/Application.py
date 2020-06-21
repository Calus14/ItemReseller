from item_scrapper.SiteScrappers import EbayScrapper, AmazonScrapper
import concurrent.futures
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/listOfItems/<searchItem>', methods=['GET'])
@cross_origin()
def findListOfItemsOrdered(searchItem):

    amazonExecutor = concurrent.futures.ThreadPoolExecutor(max_workers = 1)
    ebayExecutor = concurrent.futures.ThreadPoolExecutor(max_workers = 1)

    ebayScrapper = EbayScrapper.EbayWebScrapper()
    amazonScrapper = AmazonScrapper.AmazonScrapper()

    amazonFuture = amazonExecutor.submit( amazonScrapper.priceSearch, searchItem)
    ebayFuture = ebayExecutor.submit( ebayScrapper.priceSearch, searchItem)

    amazonItems = amazonFuture.result()
    ebayItems = ebayFuture.result()

    ebayScrapper.finish()
    amazonScrapper.finish()

    amazonItems.update(ebayItems)

    sortedItems = sorted(amazonItems.items(), key=lambda item: item[1])

    returnList = []
    for item in sortedItems:
        returnList.append( {"Name": item[0], "Price": "$"+str(item[1][0]), "Link": item[1][1] })

    jsonHelper = {"sortedItems":returnList }
    return jsonify(jsonHelper)