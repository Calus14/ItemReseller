from item_scrapper import Application
from item_scrapper.EmailManager import EmailManager
import os

''' TODO REMOVE this and place in a docker file later '''
try:
    EmailManager.userName = os.environ['EMAIL_USER']
except KeyError:
    EmailManager.userName = "itemSearcherTest@gmail.com"

try:
    EmailManager.password = os.environ['EMAIL_Password']
except KeyError:
    EmailManager.password = "wlptzpegcjasaqga"

try:
    port = os.environ['PORT']
except KeyError:
    port = 8801

Application.app.run(host='0.0.0.0', port = port, debug = True)