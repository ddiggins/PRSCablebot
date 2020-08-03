"""Module to communicate with a serial device and use and interpret JSON
   Intended to be run concurrently with another process which uses the data """

import sys
import time
from multiprocessing import Queue
import serial
import json
# TODO: Remove if uncessary: from flask_socketio import SocketIO, join_room, emit, send
from threading import Lock
from datetime import datetime

class SerialCommunication:

    def __init__(self, record_queue, pipe):
        """ Checks for serial devices on ACM ports and connects to the
            first available device. Opens a serial line and returns a reference to it """
        self.pipe = pipe
        self.record_queue = record_queue

        
        for i in range(9):
            self.ser = None
            try:
                self.ser = serial.Serial('/dev/ttyACM' + str(i), timeout=.5)
                break
            except:  # All exceptions are checked against assert below
                print('/dev/ttyACM' + str(i) + " failed. Trying next port")
        assert self.ser is not None, "Failed to connect to host (No ports open)"
        self.ser.baudrate = 115200
        # self.ser.close()
        if not self.ser.isOpen():
            self.ser.open()
        time.sleep(2)

    def send_command(self, command):
        """ Sends a command string over serial """
        self.ser.write((command + "\r\n").encode())
        # print("Writing command: " + (command + "\r\n"))
        return 1

    def receive_command(self):
        """ Reads one line from serial """
        try:
            output = self.ser.readline().decode()
            return output
        except serial.SerialException:
            print("read failed")
            return ""

    def interpret_json(self, line):
        """Interprets json and parses it into attributes"""
        # Creates dict named data with json info. Throws ValueError if
        # invalid Json input.
        try:
            data = json.loads(line)
        except json.decoder.JSONDecodeError:
            print("Failed to read a json line")
            return None

        assert 'id' in data.keys(), "Input string missing key 'id' "
        assert data['id'] != "", "Input id is empty"

        return data

    def write_to_database(self, line):
        """Write records to database"""
        data = self.interpret_json(line) #Sets updated self.data_dict
        if data is None: return
        # print("data:", data)
        current_time = datetime.now().isoformat()
        timestamp = str(current_time)
        # print("Timestamp:" + timestamp)
        # print("Data:" + str(json.dumps(data)))

        assert 'id' in data.keys(), "Input string missing key 'id' "
        assert data['id'] != "", "Input id is empty"
        
        if len(list(data.values())) == 3: # If the record has data associated
            self.record_queue.put((datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],\
                str(data["id"]), str(list(data.values())[2]))) # Add data to database
        # print("writing to the database")

    def run_communication(self):
        """ Runs a loop which reads and writes serial commands.
            Uses two queues to communicate with other processes """

        while 1:
            # Sends command from the webapp to the serial line via pipe.
            if self.pipe.poll() is True:
                self.send_command(self.pipe.recv())

            # Receives incoming messages from from serial line and writes them to the database
            response = self.receive_command()

            if response != "":
                # print("Response is:" + str(response))
                self.write_to_database(response)
            time.sleep(.005)

def start_serial_communication(record_queue, pipe):
    ser = SerialCommunication(record_queue, pipe)
    ser.run_communication()


if __name__ == "__main__":
    outgoing_commands = Queue()
    incoming_commands = Queue()
    lock = Lock()
    run_communication(incoming_commands, outgoing_commands, lock)
