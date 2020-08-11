""" A basic serial monitor to interact with an arduino """

import threading
from multiprocessing import Queue, Lock, Process, Pipe
import select
import sys
import SerialCommunication

def monitor(pipe):
    """ Takes input from the command line and sends it to an arduino then fetches the output
        This monitor works, but is really frustrating as incoming commands disturb typing"""

    while 1:
        while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            if line:
                print("Sending: " + str(line))
                pipe.send(str(line))


# Sample commands:
#{"id" : "Sensor1", "enabled" : "1"}
#{"id" : "Sensor1", "enabled" : "0"}
#{"id":"Motor1", "enabled":"0"}
#{"id":"Motor1", "enabled":"1"}
#{"id":"Motor1", "speed":"1"}
#{"id":"encoder", "enabled":"1"}
#{"id":"Motor1", "mode":"1"}
#{"id":"Motor1", "mode":"0"}
#{"id":"Motor1", "target":"0"}
# OLD: 11.6
# NEW: 12.4



if __name__ == "__main__":

    SERIAL_CHILD, SERIAL_PARENT = Pipe()
    ENCODER_CHILD, ENCODER_PARENT = Pipe()
    RECORD_QUEUE = Queue()

    COMMUNICATOR = Process(target=SerialCommunication.start_serial_communication,\
            args=(RECORD_QUEUE, SERIAL_CHILD, ENCODER_CHILD))
    COMMUNICATOR.start()

    monitor(SERIAL_PARENT)

    
