""" Module for keeping and logging data in the system """

import time
import json
from datetime import datetime

class Logger:
    """ Reads commands from serial, logs them, and reports tem to the website """

    def __init__(self, incoming_commands, outgoing_commands, lock, socketio, log_file):
        """ Creates a logger and initializes a log with the given filename """
        self.incoming_commands = incoming_commands
        self.outgoing_commands = outgoing_commands
        self.lock = lock
        self.socketio = socketio # the socketio object

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

        data = json.loads(line) # Dict type
        object_id = data["id"]
        self.socketio.emit("update", line, json = True)
        # Creates data dict with current states of objects(sensors, motors...)
        self.data_dict[object_id] = data
        
        return data

    def log_data(self, data):
        "Continually logs incoming serial messages"

        time = datetime.now().isoformat()
        timestamp = str(time)
        data = str(json.dumps(data))
        print("Timestamp:" + timestamp)
        print("Data:" + data)

        self.log_file.write(timestamp + " " + data + "\n")
        self.log_file.flush()

    
    def run_logger(self):
        """ Runs the logger continuously. Designed to be run in a separate thread """

        while 1:
            line = self.check_incoming()
            if line is not None:
                data = self.interpret_json(line)
                self.log_data(data)
            time.sleep(.05)
