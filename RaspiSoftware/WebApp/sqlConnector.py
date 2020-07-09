""" Connector for SQL database for sensor logging and data retrieval """

import mysql.connector
import time
from multiprocessing import Process, Queue, Lock

DATABASE_NAME = "sensorLogs"
DELETE_EXISTING = True

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
            self.cursor.execute("DROP TABLE IF EXISTS sensorData")

        # Create table
        self.cursor.execute("CREATE TABLE IF NOT EXISTS sensorData \
            (id INT AUTO_INCREMENT PRIMARY KEY, timestamp TIMESTAMP(3),\
                 name VARCHAR(255), value VARCHAR(255))")

    def add_data(self, timestamp, name, value):
        """ Add a row to the table
            name and value are limited to 255 char strings
            timestamp must be in format 'YYYY-MM-DD hh:mm:ss.dddd' """

        sql = "INSERT INTO sensorData (timestamp, name, value) VALUES (%s,%s,%s)"
        val = (timestamp, name, value)
        self.cursor.execute(sql, val)

        self.database.commit()
        print(self.cursor.rowcount, "record inserted.")


    def print_table(self):
        """ Prints the contents of the table (be careful with large datasets) """
        self.cursor.execute("SELECT * FROM sensorData")
        result = self.cursor.fetchall()

        for x in result:
            print(x)

    def query_sensor(self, name, num_records, order_column):
        """ Queries database for num_records recordings matching name """
        sql = "SELECT * FROM sensorData WHERE name = %s ORDER BY %s"
        adr = (name, order_column)

        self.cursor.execute(sql, adr)

        if num_records == 1:
            # To query a single value
            return self.cursor.fetchone()

        res = self.cursor.fetchall()

        if res is None:
            print("No records match this query")
            return []

        if len(res) < num_records:
            return res
        return res[:num_records]

    def run_database_connector(self, request_queue, record_queue, answer_queue):

        while 1:
            if not request_queue.empty():
                request = request_queue.get()
                assert len(request) == 3, "Invalid request entered"
                answer_queue.put(self.query_sensor(request[0], request[1], request[2]))

            if not record_queue.empty():
                data = record_queue.get()
                self.add_data(data[0], data[1], data[2])

def request_record(record, request_queue, answer_queue, lock):
    lock.acquire()
    request_queue.put(record)
    while answer_queue.empty(): time.sleep(0)
    val = answer_queue.get()
    lock.release()
    return val





if __name__ == "__main__":
    connector = SQLConnector()

    request_queue_global = Queue()
    record_queue_global = Queue()
    answer_queue_global = Queue()
    lock_global = Lock()

    # connector.add_data('1970-01-01 00:00:01.001', 'Sensor1', '5')
    # # connector.print_table()
    # print(connector.query_sensor('Sensor1', 2, 'timestamp'))

    connector = Process(target=connector.run_database_connector,\
            args=(request_queue_global, record_queue_global, answer_queue_global))
    connector.start()

    print("Record:")
    print(request_record(('Sensor1', 2, 'timestamp'), request_queue_global, answer_queue_global, lock_global))
