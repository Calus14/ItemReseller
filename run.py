from item_scrapper import Application
import os
''' TODO REMOVE this and place in a docker file later '''
os.environ['EMAIL_USER'] = "itemSearcherTest@gmail.com"
os.environ['EMAIL_PASSWORD'] = 'pythonPassword323'

Application.app.run(host='0.0.0.0', port = 8801, debug = True)