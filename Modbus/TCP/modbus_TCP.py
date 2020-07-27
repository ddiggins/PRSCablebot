""" Testing Modbus Protocol using PyModbus
    Investing running Modbus as its own process on the Pi
    https://pymodbus.readthedocs.io/en/latest/index.html """

# Import Necessary Modules for Asycronous Communication
# from twisted.internet import serialport, reactor
# from twisted.internet.protocol import ClientFactory
# from pymodbus.factory import ClientDecoder
# from pymodbus.client.asynchronous.twisted import ModbusClientProtocol

# Import Necessary Modules for Syncronous Communication
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

# Import Propper Framer (RTU -- Page 36 of Manuel)
from pymodbus.transaction import ModbusRtuFramer as ModbusFramer
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus.compat import iteritems
from collections import OrderedDict
import struct



# Configure Client Logging
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Define Device Address
UNIT = 0x0

def run_sync_client():
    """ Main loop for Modbus communication """
    # Define client connection
    client = ModbusClient('localhost', port=5020, framer=ModbusFramer)
    client.connect()

    # Specify target device
    log.debug("Reading Coils")
    rr = client.read_holding_registers(0, 7, unit=UNIT)
    log.debug(rr.registers)
    log.debug(rr.registers[0])
    decoder = BinaryPayloadDecoder.fromRegisters(rr.registers,
                                                 byteorder=Endian.Big)
    
    decoded = OrderedDict([
        ('value', decoder.decode_32bit_float()),
        ('qualityId', decoder.decode_16bit_uint()),
        ('unitId', decoder.decode_16bit_float()),
        ('paramId', decoder.decode_16bit_uint()),
        ('sentinel', decoder.decode_32bit_float())
    ])

    for name, value in iteritems(decoded):
        log.debug(name)
        log.debug(value)

    # Close Client
    client.close()

if __name__ == "__main__":
    run_sync_client()