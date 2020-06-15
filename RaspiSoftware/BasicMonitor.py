# A basic serial monitor to interact with an arduino

import serial
import time
import threading
from multiprocessing import Queue
import json
import select
import sys
import SerialCommunication

def monitor(outgoing_queue, incoming_queue):
    """ Takes input from the command line and sends it to an arduino then fetches the output """

    while 1:
        while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            if line:
                outgoing_queue.put(line)
        
        if not incoming_queue.empty():
            line = incoming_queue.get_nowait()
            if line is not '':
                print(line)


#{"id" : "Sensor1", "enabled" : "1"}
#{"id" : "Sensor1", "enabled" : "0"}





















if __name__ == "__main__":
    outgoing_commands = Queue()
    incoming_commands = Queue()
    communicator = threading.Thread(target=SerialCommunication.run_communication, args=(outgoing_commands, incoming_commands))
    communicator.start()
    monitor(outgoing_commands, incoming_commands)