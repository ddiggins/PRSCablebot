
import minimalmodbus
import serial
import time
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # port name, slave address (in decimal)
instrument.serial.parity = serial.PARITY_EVEN

# write_file = open("registers.txt", 'w')
instrument.serial.timeout  = 2         # seconds


try:
    instrument.read_register(0) # Wake up sensor
except:
    time.sleep(1)

# print(instrument.read_bits(9001, 32))
# print(instrument.read_bits(9006, 16, functioncode=1))
print(instrument.read_registers(9006, 2))
print(instrument.read_registers(9006, 2))
print(instrument.read_registers(9018, 32))
print(instrument.read_registers(5450, 7))



# from pymodbus.client.sync import ModbusSerialClient as ModbusClient

# # Import Propper Framer (RTU -- Page 36 of Manuel)
# from pymodbus.transaction import ModbusRtuFramer as ModbusFramer

# from pymodbus.payload import BinaryPayloadDecoder
# from pymodbus.constants import Endian
# from pymodbus.compat import iteritems
# from pymodbus import exceptions as modbusexceptions
# from pymodbus.other_message import *
# from collections import OrderedDict
# import struct
# import logging
# from datetime import datetime


# client = ModbusClient(method='rtu', port="/dev/ttyUSB0", timeout=1, baudrate=19200)

# client.connect()

# print(client.read_holding_registers(45450, 7))
# # print(client.read_holding_registers(45450, 7))
# print(client.read_holding_registers(0))