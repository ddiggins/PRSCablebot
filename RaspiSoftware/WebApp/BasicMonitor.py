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
                pipe.send(line)


# Sample commands:
#{"id" : "Sensor1", "enabled" : "1"}
#{"id" : "Sensor1", "enabled" : "0"}


if __name__ == "__main__":

    SERIAL_CHILD, SERIAL_PARENT = Pipe()

    COMMUNICATOR = Process(target=SerialCommunication.start_serial_communication,\
            args=(None, SERIAL_CHILD))
    COMMUNICATOR.start()

    monitor(SERIAL_PARENT)
