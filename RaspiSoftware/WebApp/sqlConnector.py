""" Connector for SQL database for sensor logging and data retrieval """

import mysql.connector
import time
from multiprocessing import Process, Queue, Lock

# DATABASE_NAME = "sensorLogs"
# DELETE_EXISTING = False

class SQLConnector:

    """ A wrapper for mySQL to handle data dumps and requests """

    def __init__(self, database_name, table_name, delete_existing, lock):
        """ Set up database if not alrerady configured and assign structure """

        self.lock = lock
        # Connect to server and create cursor
        self.database = mysql.connector.connect(
            host="localhost",
            user="databaseUser",
            password="user",
            database=database_name
            )
        self.cursor = self.database.cursor()

        # Clear table if specified
        self.table_name = table_name
        if delete_existing:
            self.cursor.execute("DROP TABLE IF EXISTS " + str(self.table_name))

        # Create table
        self.cursor.execute("CREATE TABLE IF NOT EXISTS " + str(self.table_name) \
            + " (id INT AUTO_INCREMENT PRIMARY KEY, timestamp TIMESTAMP(3),\
                 name VARCHAR(255), value VARCHAR(255))")

    def add_data(self, timestamp, name, value):
        """ Add a row to the table
            name and value are limited to 255 char strings
            timestamp must be in format 'YYYY-MM-DD hh:mm:ss.dddd' """

        sql = "INSERT INTO " + str(self.table_name) + " (timestamp, name, value) VALUES (%s,%s,%s)"
        val = (timestamp, name, value)
        self.cursor.execute(sql, val)

        self.database.commit()
        print(self.cursor.rowcount, "record inserted.")
        return self.cursor.rowcount


    def print_table(self):
        """ Prints the contents of the table (be careful with large datasets) """
        self.cursor.execute("SELECT * FROM " + str(self.table_name))
        result = self.cursor.fetchall()

        for x in result:
            print(x)

    def query_sensor(self, name, num_records, order_column):
        """ Queries database for num_records recordings matching name """
        sql = "SELECT * FROM " + str(self.table_name) + " WHERE name = %s ORDER BY %s"
        adr = (name, order_column)

        self.cursor.execute(sql, adr)

        print("NUM RECORDS IS " + str(num_records))
        print("TYPE OF NUM_RECORDS IS " + str(type(num_records)))

        if num_records == 1:
            # To query a single value
            return self.cursor.fetchone()

        res = self.cursor.fetchall()

        if res is None:
            print("No records match this query")
            return []

        if len(res) < num_records:
            return res
        return res[:num_records+1]

    def run_database_connector(self, request_queue, record_queue, answer_queue):

        while 1:
            if not request_queue.empty():
                request = request_queue.get()
                assert len(request) == 3, "Invalid request entered"
                answer_queue.put(self.query_sensor(request[0], request[1], request[2]))

            self.lock.acquire()
            if not record_queue.empty():
                print("INSERTING RECORD")
                data = record_queue.get()
                self.add_data(data[0], data[1], data[2])
            self.lock.release()
            time.sleep(0)

def request_record(record, request_queue, answer_queue, lock):
    """ Requests one or more records from the database """
    lock.acquire()
    request_queue.put(record)
    while answer_queue.empty(): time.sleep(0) # yield
    val = answer_queue.get()
    lock.release()
    return val

def add_record(record, record_queue, lock):
    """ Requests one or more records from the database """
    lock.acquire()
    record_queue.put(record)
    lock.release()





if __name__ == "__main__":
    connector = SQLConnector("sensorLogs", "testData", True)

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
    lock_global.acquire()
    record_queue_global.put(('2000-01-01 00:00:01.000', "testName", "testValue"))
    record_queue_global.put(('2000-01-01 00:00:01.000', "testName", "testValue"))
    lock_global.release()

    print("Record:")
    print(request_record(('testName', 2, 'timestamp'), request_queue_global, answer_queue_global, lock_global))
