""" Connector for SQL database for sensor logging and data retrieval """

import mysql.connector
import time
from multiprocessing import Process, Queue, Lock
import datetime
import json


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


        if table_name == "default": # Default assigns a new unique number

            self.cursor.execute("SHOW TABLES")
            a = self.cursor.fetchall()

            tables = [x[0] for x in a if x[0][3:].isnumeric()] # Fetch names of all numbered tables
            tables.sort()

            if tables == []:
                new_table_name = "run0"
            else:
                new_table_name = "run" + str(int(tables[-1][3:]) + 1) # Create new name one greater than existing
            self.table_name = new_table_name

        else:
            self.table_name = table_name


        # Clear table if specifiedTrueTrue
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

        # Check for errors in inputs
        # Verify that inputs are strings
        assert isinstance(timestamp, str) and isinstance(name, str) and isinstance(value, str),\
             "Inputs must be of type string"
        #Verify that inputs do not overflow allowed size
        assert len(timestamp) <= 255 and len(name) <= 255 and len(value) <= 255,\
             "Input string overflow, (max 255 chars)"
        # Verify that timestamp conforms to proper format
        try:
            datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            raise ValueError("Incorrect data format, should be 'Y-m-d H:M:S.f'")

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


    def query_sensor(self, name, num_records, order_column, table_name="default"):
        """ Queries database for num_records recordings matching name """
        if table_name == "default":
            sql = "SELECT * FROM " + str(self.table_name) + " WHERE name = %s ORDER BY %s"
        else:
            sql = "SELECT * FROM " + str(table_name) + " WHERE name = %s ORDER BY %s"
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
        """ Check for incoming requests and process them """
        while 1:
            if not request_queue.empty():
                request = request_queue.get()
                assert len(request) == 3 or len(request) == 4, "INVALID REQUEST: wrong number of arguments"
                if len(request) == 3:
                    answer_queue.put(self.query_sensor(request[0], request[1], request[2]))
                if len(request) == 4:
                    answer_queue.put(self.query_sensor(request[0], request[1], request[2], request[3]))

            self.lock.acquire()
            if not record_queue.empty():
                print("INSERTING RECORD")
                data = record_queue.get()
                self.add_data(data[0], data[1], data[2])
            self.lock.release()
            time.sleep(.01)


def request_record(record, request_queue, answer_queue, lock):
    """ Requests one or more records from the database 
    record: (name of variable, number of records wanted, sorted by)
    """
    
    request_queue.put(record)
    # while answer_queue.empty(): time.sleep(.01) # yield
    while 1:
        lock.acquire()
        if answer_queue.empty():
            lock.release()
            break
        lock.release()
        time.sleep(.01)

    val = answer_queue.get()
    return val


def add_record(record, record_queue, lock):
    """ Requests one or more records from the database """
    lock.acquire()
    record_queue.put(record)
    lock.release()


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

if __name__ == "__main__":
    REQUEST_QUEUE_GLOBAL = Queue()
    RECORD_QUEUE_GLOBAL = Queue()
    ANSWER_QUEUE_GLOBAL = Queue()
    LOCK_GLOBAL = Lock()

    CONNECTOR = SQLConnector("sensorLogs", "testData", True, LOCK_GLOBAL)


    # CONNECTOR.add_data('1970-01-01 00:00:01.001', 'Sensor1', '5')
    # # CONNECTOR.print_table()
    # print(CONNECTOR.query_sensor('Sensor1', 2, 'timestamp'))

    CONNECTOR = Process(target=CONNECTOR.run_database_connector,\
        args=(REQUEST_QUEUE_GLOBAL, RECORD_QUEUE_GLOBAL, ANSWER_QUEUE_GLOBAL))
    CONNECTOR.start()

    # Adding records
    # RECORD_QUEUE_GLOBAL.put(('2000-01-01 00:00:01.000', "testName", "testValue"))
    # RECORD_QUEUE_GLOBAL.put(('2000-01-01 00:00:02.000', "testName", "testValue"))
    add_record(('2000-01-01 00:00:01.000', "testName", "testValue"),\
        RECORD_QUEUE_GLOBAL, LOCK_GLOBAL)
    add_record(('2000-01-01 00:00:01.000', "testName", "testValue"), \
        RECORD_QUEUE_GLOBAL, LOCK_GLOBAL)

    while not RECORD_QUEUE_GLOBAL.empty(): time.sleep(.01)
    time.sleep(.5)
    print("about to get record")
    RECORD = request_record(('testName', 1, 'timestamp'), REQUEST_QUEUE_GLOBAL, ANSWER_QUEUE_GLOBAL, LOCK_GLOBAL)
    #
    print("queried record type: ", type(RECORD))
    jsonRecord = json.dumps(RECORD, default = myconverter)
    print("json record: ", jsonRecord)
    #
    print("got record")
    print("record is" + str(RECORD))
    CONNECTOR.kill()
    print(RECORD)
