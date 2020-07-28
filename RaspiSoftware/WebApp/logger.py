""" Module for keeping and logging data in the system """
import json
from datetime import datetime
import sqlConnector
from flask_socketio import SocketIO, emit, send
import time

class Logger:
    """ Reads commands from serial, logs them, and reports them to the website """

    def __init__(self, incoming_commands, outgoing_commands, lock, socketio, log_file,\
        connector_queues):
        """ Creates a logger and initializes a log with the given filename """
        self.incoming_commands = incoming_commands
        self.outgoing_commands = outgoing_commands
        self.lock = lock
        self.socketio = socketio # the socketio object
        self.connector_queues = connector_queues

        # Define data structure
        # Dictionary of all current data known to the system
        # Keys are object id and values are dictionaries that describe the object's state
        self.data_dict = {}

        # Initialize log file
        self.log_file_name = log_file
        self.log_file = open(self.log_file_name, "a")
        self.log_file.write('\n\n\n{"App Status": "Starting App"}' + "\n")
        self.log_file.flush()

    def check_incoming(self):
        """Function that checks whether there are new incoming serial messages.
        Returns None if the buffer is empty"""
        self.lock.acquire()
        line = None
        if not self.incoming_commands.empty():
            line = self.incoming_commands.get_nowait()
        self.lock.release()
        return line

    def interpret_json(self, line):
        """Interprets json and parses it into attributes"""
        # Creates dict named data with json info. Throws ValueError if
        # invalid Json input.
        data = json.loads(line)

        assert 'id' in data.keys(), "Input string missing key 'id' "
        assert data['id'] != "", "Input id is empty"

        if 'id' in data:
            object_id = data["id"]
            # self.socketio.emit("update", line, json=True)
            self.socketio.emit("update", line, json=True)

            # Creates data dict with current states of objects(sensors, motors...)
            self.data_dict[object_id] = data
        return data

    def log_data(self, data_dict):
        "Continually logs incoming serial messages"

        current_time = datetime.now().isoformat()
        timestamp = str(current_time)
        data = str(json.dumps(data_dict))
        print("Timestamp:" + timestamp)
        print("Data:" + data)

        assert 'id' in data_dict.keys(), "Input string missing key 'id' "
        assert data_dict['id'] != "", "Input id is empty"

        self.log_file.write(timestamp + " " + data + "\n")
        self.log_file.flush()

        # Write records to database
        if len(list(data_dict.values())) == 3: # If the record has data associated
            self.connector_queues[1].put((datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],\
                str(data_dict["id"]), str(list(data_dict.values())[2]))) # Add data to database
        print("writing to the database")

    def run_logger(self):
        """ Runs the logger continuously. Designed to be run in a separate thread """

        while 1:
            line = self.check_incoming()
            if line is not None:
                data = self.interpret_json(line)
                self.log_data(data)
            time.sleep(.05)
