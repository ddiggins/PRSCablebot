""" Connector for SQL database for sensor logging and data retrieval """

import mysql.connector

DATABASE_NAME = "sensorLogs"
DELETE_EXISTING = False

class SQLConnector:

    """ A wrapper for mySQL to handle data dumps and requests """

    def __init__(self):
        """ Set up database if not alrerady configured and assign structure """

        # Connect to server and create cursor
        self.database = mysql.connector.connect(
            host="localhost",
            user="databaseUser",
            password="user",
            database=DATABASE_NAME
            )
        self.cursor = self.database.cursor()

        # Clear table if specified
        if DELETE_EXISTING:
            self.cursor.execute("DELETE TABLE IF EXISTS sensorData")

        # Create table
        self.cursor.execute("CREATE TABLE IF NOT EXISTS sensorData (id INT AUTO_INCREMENT PRIMARY KEY, timestamp TIMESTAMP(3), name VARCHAR(255), value VARCHAR(255))")

        # self.cursor.execute("SHOW TABLES")
        # print("tables:")
        # for x in self.cursor:
        #     print(x)

    def add_data(self, timestamp, name, value):
        sql = "INSERT INTO sensorData (timestamp, name, value) VALUES (%s,%s,%s)"
        val = (timestamp, name, value)
        self.cursor.execute(sql, val)

        self.database.commit()
        print(self.cursor.rowcount, "record inserted.")


    def print_table(self):

        self.cursor.execute("SELECT * FROM sensorData")
        result = self.cursor.fetchall()

        for x in result:
            print(x)


if __name__ == "__main__":
    connector = SQLConnector()

    connector.add_data('1970-01-01 00:00:01.001', 'Sensor1', '5')
    connector.print_table()
