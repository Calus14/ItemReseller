import EbayScrapper
import AmazonScrapper
import concurrent.futures
import time

amazonExecutor = concurrent.futures.ThreadPoolExecutor(max_workers = 1)
ebayExecutor = concurrent.futures.ThreadPoolExecutor(max_workers = 1)

ebayScrapper = EbayScrapper.EbayWebScrapper()
amazonScrapper = AmazonScrapper.AmazonScrapper()

amazonFuture = amazonExecutor.submit( amazonScrapper.priceSearch, "Air Jordans" )
ebayFuture = ebayExecutor.submit( ebayScrapper.priceSearch, "Air Jordans" )

while(amazonFuture.running() or ebayFuture.running()):
    time.sleep(1)

amazonItems = amazonFuture.result()
ebayItems = ebayFuture.result()

ebayScrapper.finish()
amazonScrapper.finish()

amazonItems.update(ebayItems)

sortedItems = sorted(amazonItems.items(), key=lambda item: item[1])

sortedDict = {}
for item in sortedItems:
    sortedDict[item[0]] = item[1]

print("The Final combined list of items is as follows")
for item in sortedDict:
    print(item + " Priced at " + str(sortedDict[item]) )