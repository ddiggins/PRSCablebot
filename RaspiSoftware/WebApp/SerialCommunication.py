"""Module to communicate with a serial device and use and interpret JSON
   Intended to be run concurrently with another process which uses the data """

import time
from multiprocessing import Queue
import serial

def start_serial():
    """ Checks for serial devices on ACM ports and connects to the
        first available device. Opens a serial line and returns a reference to it """
    for i in range(9):
        ser = None
        try:
            ser = serial.Serial('/dev/ttyACM' + str(i), timeout=.1)
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

def receive_command(ser):
    """ Reads one line from serial """
    output = ser.readline().decode()
    return output

def run_communication(input_commands, output_commands):
    """ Runs a loop which reads and writes serial commands.
        Uses two queues to communicate with other processes """

    ser = start_serial()
    while 1:

        if not input_commands.empty():
            command = input_commands.get_nowait()
            socketio.emit('new incoming', broadcast=True)

        else:
            command = None
        if command is not None:
            send_command(ser, command)

        response = receive_command(ser)
        output_commands.put(response)

        time.sleep(.005)


if __name__ == "__main__":
    outgoing_commands = Queue()
    incoming_commands = Queue()
    run_communication(incoming_commands, outgoing_commands)