
import minimalmodbus
import serial
import time
import numpy as np
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # port name, slave address (in decimal)
instrument.serial.parity = serial.PARITY_EVEN

# write_file = open("registers.txt", 'w')
instrument.serial.timeout = 2         # seconds


try:
    instrument.read_register(0) # Wake up sensor
except:
    time.sleep(1)

# print(instrument.read_bits(9001, 32))
# print(instrument.read_bits(9006, 16, functioncode=1))
print(instrument.read_registers(9006, 2))
print(instrument.read_registers(9006, 2))
print(instrument.read_registers(9018, 32))
request = instrument.read_registers(5450, 7)

# value = np.array([(request[0] << 16) + request[1]], dtype=np.uint32)
# value = value.view(np.single).item(0)
# quality_id = request[2]
# unit_id = request[3]
# param_id = request[4]
# sentinel = np.array([(request[5] << 16) + request[6]], dtype=np.uint32)
# sentinel = sentinel.view(np.single).item(0)

# data = {'value':value, 'quality_id':quality_id, 'unit_id':unit_id, 'param_id':param_id, 'sentinel':sentinel}
# print(data)

def get_bit(num, n):
        return (num >> n) & 1

res = instrument.read_registers(6983, 14)

sensors = []
for i in res:
    for j in range(16):
        sensors.append(get_bit(i, j))
print(sensors)


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


# client = ModbusClient(method='rtu', port="/dev/ttyUSB0", timeout=2, baudrate=19200)

# client.connect()

# print(client.read_holding_registers(45450, 7))
# # print(client.read_holding_registers(45450, 7))
# print(client.read_holding_registers(0))