from flask_mail import Mail, Message
import os
class EmailBroker:

    myMailer = None
    flaskApp = None
    userName = None
    password = None

    def __init__(self, flaskApp):
        self.flaskApp = flaskApp
        mail_settings = {
            "MAIL_SERVER": 'smtp.gmail.com',
            "MAIL_PORT": 465,
            "MAIL_USE_TLS": False,
            "MAIL_USE_SSL": True,
            "MAIL_USERNAME": self.userName,
            "MAIL_PASSWORD": self.password
        }

        self.flaskApp.config.update(mail_settings)
        self.myMail = Mail(flaskApp)


    def sendEmail(self, websiteItem, emailUser):
        with self.flaskApp.app_context():
            #For whatever reason this makes a tuple
            msgBody = "<pre>A matching item has been found for you! \nThe item is listed as: "+websiteItem.itemName+" \n It is priced at "+str(websiteItem.itemPrice)+"\n <a href=\""+websiteItem.itemLink+"\">Click here to view the item Listing<\a>\n Thank you very much!</pre>",

            emailMessage = Message("Item Found At Your Price",
                                   sender=self.flaskApp.config.get("MAIL_USERNAME"),
                                   html=msgBody[0],
                                   recipients=[emailUser],
                                   )

            self.myMail.send(emailMessage)