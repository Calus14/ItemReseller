import unittest
import validators
import item_scrapper.SiteScrappers.WalmartScrapper as WalmartScrapper
import item_scrapper.SiteScrappers.BestBuyScrapper as BestBuyScrapper
import item_scrapper.SiteScrappers.EbayScrapper as EbayScrapper
import item_scrapper.SiteScrappers.TargetScrapper as TargetScrapper
import item_scrapper.SiteScrappers.NeweggScrapper as NeweggScrapper

def basic_scrapper_test(scrapper, item):
    filledItems = scrapper.scrapeWebsite(item)
    passed = True
    passed &= (len(filledItems) > 0 )
    for item in filledItems:
        passed &= len(item.itemName) > 0
        passed &= item.itemPrice != None
        passed &= validators.url(item.itemLink)

    return passed


class ScrapperTest(unittest.TestCase):
    def test_basic_scrappers(self):
        testItem = "Led"
        self.assertTrue( basic_scrapper_test(WalmartScrapper.WalmartScrapper(), testItem))
        self.assertTrue( basic_scrapper_test(BestBuyScrapper.BestBuyScrapper(), testItem))
        self.assertTrue( basic_scrapper_test(EbayScrapper.EbayScrapper(), testItem))
        #TODO Fix target not loading the search request i think its because i need to render the java script but requests-html doesnt support multithreading
        #self.assertTrue( basic_scrapper_test(TargetScrapper.TargetScrapper(), testItem))
        self.assertTrue( basic_scrapper_test(NeweggScrapper.NeweggScrapper(), testItem))

if __name__ == '__main__':
    unittest.main()
