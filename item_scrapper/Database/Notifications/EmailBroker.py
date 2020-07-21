from flask_mail import Mail, Message
import os
class EmailBroker:

    myMailer = None
    flaskApp = None
    userName = "notifications@imbrokebutwantit.com"
    password = "P4ssw0rd1!"

    def __init__(self, flaskApp):
        self.flaskApp = flaskApp
        if( "EMAILUSERNAME" in os.environ):
            self.userName = os.getenv("EMAILUSERNAME")
        if( "EMAILPASSWORD" in os.environ):
            self.password = os.getenv("EMAILPASSWORD")

        mail_settings = {
            "MAIL_SERVER": 'smtp.emailmg.domain.com',
            "MAIL_PORT": 465,
            "MAIL_USE_TLS": False,
            "MAIL_USE_SSL": True,
            "MAIL_USERNAME": self.userName,
            "MAIL_PASSWORD": self.password
        }

        self.flaskApp.config.update(mail_settings)
        self.myMail = Mail(flaskApp)


    def sendEmail(self, websiteItems, emailUser, itemName):
        with self.flaskApp.app_context():
            if len(websiteItems) == 0:
                return
            #For whatever reason this makes a tuple
            msgBody = "<pre><h3>This Email is from ImBrokeButWantIt.com</h3>\n"
            msgBody = msgBody + "\n You have an active search for the anything returned under "+itemName+" within a set dollar amount or percentage of the market average.\n"
            msgBody = msgBody + "The following items have been found to match this result:\n "
            for item in  websiteItems:
                msgBody = msgBody + "<a href=\""+item.itemLink+"\">"+item.itemName+"</a> : Priced at <b>"+str(item.itemPrice)+"$</b>\n\n "

            msgBody = msgBody + "Thank you very much, Hope this helps!\n Sincerly, Big Chungus</pre>"

            emailMessage = Message("Your Subscribed Search For "+itemName+" has found some items!",
                                   sender=self.flaskApp.config.get("MAIL_USERNAME"),
                                   html=msgBody,
                                   recipients=[emailUser],
                                   )

            self.myMail.send(emailMessage)