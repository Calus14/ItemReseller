from item_scrapper import FlaskApplication
from item_scrapper import SocketioServer
from item_scrapper.Database.Notifications.EmailBroker import EmailBroker
import os

''' TODO REMOVE this and place in a docker file later '''
try:
    EmailBroker.userName = os.environ['EMAIL_USER']
except KeyError:
    EmailBroker.userName = "itemSearcherTest@gmail.com"

try:
    EmailBroker.password = os.environ['EMAIL_Password']
except KeyError:
    EmailBroker.password = "wlptzpegcjasaqga"

try:
    port = os.environ['PORT']
except KeyError:
    port = 8801


SocketioServer.socketio.run(FlaskApplication.app, host='0.0.0.0', port = port, debug = True)
print(SocketioServer.socketio.server)