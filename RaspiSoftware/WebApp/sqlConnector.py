""" Connector for SQL database for sensor logging and data retrieval """
import mysql.connector
import time
from multiprocessing import Process, Queue, Lock
import datetime
import json
from flask_socketio import SocketIO, emit, send

class SQLConnector:
    """ A wrapper for mySQL to handle data dumps and requests """

    # def __init__(self, database_name, table_name, delete_existing, lock):
    def __init__(self, database_name, table_name, delete_existing):

        """ Set up database if not alrerady configured and assign structure """

        
        self.socketio = SocketIO(message_queue='redis://')  # the socketio object

        # Connect to server and create cursor
        self.database = mysql.connector.connect(
            host="localhost",
            user="databaseUser",
            password="user",
            database=database_name
            )
        self.cursor = self.database.cursor(buffered=True)
        

        if table_name == "default": # Default assigns a new unique number

            self.cursor.execute("SHOW TABLES")
            a = self.cursor.fetchall()

            tables = [x[0] for x in a if x[0][3:].isnumeric()] # Fetch names of all numbered tables
            # Sort tables in ascending order
            tables.sort(key=lambda x: int("".join([i for i in x if i.isdigit()])))

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
        
        # Create dummy placeholder line.
        
        self.add_data('2000-01-01 00:00:01.000', "dummyName", "dummyValue")


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
        # print(self.cursor.rowcount, "record inserted.")
        return self.cursor.rowcount


    def print_table(self):
        """ Prints the contents of the table (be careful with large datasets) """
        self.cursor.execute("SELECT * FROM " + str(self.table_name))
        result = self.cursor.fetchall()

        for x in result:
            print(x)


    def query_sensor(self, name, num_records, order_column, table_name="default"): # add in default to generate new tables
        """ Queries database for num_records recordings matching name. 

        To just select the n last rows regardless of name, set name = "*"
        """
        # "default" signifies that new tables are created each run, 
        # so query selects from the latest table
        if table_name == "default":
            if name == "*": 
                sql = "SELECT * FROM " + str(self.table_name) + " ORDER BY id DESC"
            else:
                sql = "SELECT * FROM " + str(self.table_name) + " WHERE name = %s ORDER BY %s"

        else:
            if name == "*":
                sql = "SELECT * FROM " + str(table_name) + " ORDER BY id DESC"
            else:
                sql = "SELECT * FROM " + str(table_name) + " WHERE name = %s ORDER BY %s"

        if name == "*":
            # adr = (order_column)
            # self.cursor.execute(sql, adr)
            self.cursor.execute(sql)

        else:
            adr = (name, order_column)
            self.cursor.execute(sql, adr)

        # print("NUM RECORDS IS " + str(num_records))
        # print("TYPE OF NUM_RECORDS IS " + str(type(num_records)))

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


    def run_database(self, record_queue):
        """ Check for incoming requests and process them """
        print ("running database")
        # Setting old record so the newly retrieved ones have something to compare to
        old_record = self.query_sensor('*', 1, 'timestamp')
        while 1:

            # Write into database
            if not record_queue.empty():
                # print("INSERTING RECORD")
                data = record_queue.get()
                self.add_data(data[0], data[1], data[2])

            time.sleep(0.01)

            # reading database for frontend table display
            new_record = self.query_sensor('*', 1, 'timestamp')
            # print ("NEW RECORD: ", new_record)
            # print ("OLD RECORD: ", old_record)
            
            # Check that the record has updated.
            record_equality = (new_record == old_record)
            # print ("RECORD EQUALITY: ", record_equality)
            # if (new_record != old_record):
            if (record_equality == False):
                # Update old record to new record since we already compared them
                old_record = new_record
                # Removes id of record, reorders so that the sensor name is first.
                # (name, value, timestamp)
                new_record = (new_record[2], new_record[3], new_record[1])
                new_record = json.dumps(new_record, default = myconverter) # Converts into Json
                # print("json new record: ", new_record)
                self.socketio.emit("update table", new_record, broadcast = True)
                # print("emited update table")
    
def add_record(record, record_queue, lock):
    """ Add record to the database """
    lock.acquire()
    record_queue.put(record)
    lock.release()

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def start_sqlConnector(record_queue):
    connector = SQLConnector("sensorLogs", "default", False)
    connector.run_database(record_queue)

if __name__ == "__main__":
    # REQUEST_QUEUE_GLOBAL = Queue()
    # RECORD_QUEUE_GLOBAL = Queue()
    # ANSWER_QUEUE_GLOBAL = Queue()
    # LOCK_GLOBAL = Lock()

    # CONNECTOR = SQLConnector("sensorLogs", "testData", True, LOCK_GLOBAL, socketio)


    # # CONNECTOR.add_data('1970-01-01 00:00:01.001', 'Sensor1', '5')
    # # # CONNECTOR.print_table()
    # # print(CONNECTOR.query_sensor('Sensor1', 2, 'timestamp'))

    # CONNECTOR = Process(target=CONNECTOR.run_database_connector,\
    #     args=(REQUEST_QUEUE_GLOBAL, RECORD_QUEUE_GLOBAL, ANSWER_QUEUE_GLOBAL))
    # CONNECTOR.start()

    # # Adding records
    # # RECORD_QUEUE_GLOBAL.put(('2000-01-01 00:00:01.000', "testName", "testValue"))
    # # RECORD_QUEUE_GLOBAL.put(('2000-01-01 00:00:02.000', "testName", "testValue"))
    # add_record(('2000-01-01 00:00:01.000', "testName", "testValue"),\
    #     RECORD_QUEUE_GLOBAL, LOCK_GLOBAL)
    # add_record(('2000-01-01 00:00:01.000', "testName", "testValue"), \
    #     RECORD_QUEUE_GLOBAL, LOCK_GLOBAL)

    # while not RECORD_QUEUE_GLOBAL.empty(): time.sleep(.01)
    # time.sleep(.5)
    # print("about to get record")
    # RECORD = request_record(('testName', 1, 'timestamp'), REQUEST_QUEUE_GLOBAL, ANSWER_QUEUE_GLOBAL, LOCK_GLOBAL)
    # print("record is" + str(RECORD))
    
    # # Testing for json data to feed into Google Charts
    # print("queried record type: ", type(RECORD)) #This is a tuple
    # # jsonRecord = RECORD[1:] #Removes the first element because it's just the ID.
    # rearranged_record = (RECORD[2], RECORD[3], RECORD[1])
    # jsonRecord = json.dumps(rearranged_record, default = myconverter)
    # print("json record: ", jsonRecord)
    # # # Convert json back to tuple
    # # oldjson = json.loads()

    # # Get latest n records
    # LATESTRECORD = request_record(('*', 1, 'timestamp'), REQUEST_QUEUE_GLOBAL, ANSWER_QUEUE_GLOBAL, LOCK_GLOBAL)
    # print("latest record: ", LATESTRECORD)
    # print("latest record type: ", type(LATESTRECORD))
    # #

    # CONNECTOR.kill()
    pass
