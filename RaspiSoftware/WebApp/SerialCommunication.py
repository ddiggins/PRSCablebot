"""Module to communicate with a serial device and use and interpret JSON
   Intended to be run concurrently with another process which uses the data """

import sys
import time
from multiprocessing import Queue
import serial
from flask_socketio import SocketIO, join_room, emit, send
from threading import Lock


def start_serial():
    """ Checks for serial devices on ACM ports and connects to the
        first available device. Opens a serial line and returns a reference to it """
    for i in range(9):
        ser = None
        try:
            ser = serial.Serial('/dev/ttyACM' + str(i), timeout=.5)
            break
        except:  # All exceptions are checked against assert below
            print('/dev/ttyACM' + str(i) + " failed. Trying next port")
    assert ser is not None, "Failed to connect to host (No ports open)"
    ser.baudrate = 115200
    ser.close()
    ser.open()
    time.sleep(2)
    return ser

def send_command(ser, command):
    """ Sends a command string over serial """
    ser.write((command + "\r\n").encode())
    print("writing Command")
    print("Command written: " + (command + "\r\n"))

def receive_command(ser):
    """ Reads one line from serial """
    try:
        output = ser.readline().decode()
        return output

    except serial.SerialException:
        print ("read failed")
        return ""

def run_communication(input_commands, output_commands, lock):
    """ Runs a loop which reads and writes serial commands.
        Uses two queues to communicate with other processes """

    ser = start_serial()

    f = open("log1.txt", "w")

    while 1:

        lock.acquire()

        if not input_commands.empty():
            command = input_commands.get_nowait()

        else:
            command = None
        if command is not None:
            send_command(ser, command)

        response = receive_command(ser)
        print("Response is:" + str(response))
        f.write("Response is:" + str(response))
        output_commands.put(response)
        lock.release()

        time.sleep(.005)



if __name__ == "__main__":
    outgoing_commands = Queue()
    incoming_commands = Queue()
    lock = Lock()
    run_communication(incoming_commands, outgoing_commands, lock)