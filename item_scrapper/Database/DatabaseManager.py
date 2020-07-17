import psycopg2
import psycopg2.extras
import os

class DatabaseManager:

    databaseHost = "localhost"
    databaseName = "itemResellerDatabase"
    username = "postgres"
    password = "Frontfull1"
    port = 5432

    databaseConnection = None

    def __init__(self):
        if( "DATABASEHOST" in os.environ):
            self.databaseHost = os.getenv("DATABASEHOST")
        if( "DATABASENAME" in os.environ):
            self.databaseName = os.getenv("DATABASENAME")
        if( "USERNAME" in os.environ):
            self.username = os.getenv("USERNAME")
        if( "PASSWORD" in os.environ):
            self.password = os.getenv("PASSWORD")
        if( "PORT" in os.environ):
            self.port = os.getenv("PORT")

        psycopg2.extras.register_uuid()

        self.databaseConnection = psycopg2.connect(
                            host = self.databaseHost,
                            database = self.databaseName,
                            user = self.username,
                            password = self.password,
                            port = self.port
        )

        # TODO Any change to tables will have to have migration code run on heroku after this call
        self.createTablesIfNeeded()

    def createTablesIfNeeded(self):
        tableCommands = (
            """
            CREATE TABLE IF NOT EXISTS  users (
                user_id UUID PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                user_password VARCHAR(255) NOT NULL,
                CONSTRAINT userEmailKey UNIQUE(user_email),
                creation_time TIME  NOT NULL
            )
            """,
            """ CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id UUID PRIMARY KEY,
                user_id UUID NOT NULL,
                item_name VARCHAR(255) NOT NULL,
                price_point NUMERIC(20, 10) NOT NULL,
                price_type VARCHAR(255),
                creation_time TIME  NOT NULL,
                expiration_time TIME NOT NULL,
                CONSTRAINT userItemKey UNIQUE(user_id, item_name),
                FOREIGN KEY (user_id)
                    REFERENCES users (user_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
                )
            """,
            """
            CREATE TABLE IF NOT EXISTS items (
                    item_name VARCHAR(255) PRIMARY KEY,
                    average_item_price NUMERIC(20, 10)
            )
            """
        )

        cursor = self.databaseConnection.cursor()
        for command in tableCommands:
            cursor.execute(command)

        cursor.close()
        self.databaseConnection.commit()

    def finish(self):
        self.databaseConnection.close()