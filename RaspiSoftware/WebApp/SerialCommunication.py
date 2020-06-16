# Module to communicate with a serial device and use and interpret JSON
# Intended to be run concurrently with another process which uses the data


import serial
import time
import threading
from multiprocessing import Queue
import json

def start_serial():
    for i in range(9):
        ser = None
        try:
            ser = serial.Serial('/dev/ttyACM' + str(i), timeout=.1)
            break
        except:
            print('/dev/ttyACM' + str(i) + " failed. Trying next port")
    assert ser is not None, "Failed to connect to host (No ports open)"
    ser.baudrate = 115200
    ser.close()
    ser.open()
    time.sleep(2)
    return ser

def send_command(ser, command):
    ser.write((command + "\r\n" ).encode())
    print("writing Command")

def receive_command(ser):
    output = ser.readline().decode()
    return output

def run_communication(input_commands, output_commands):
    ser = start_serial()
    while 1:

        if not input_commands.empty():
            command = input_commands.get_nowait()
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