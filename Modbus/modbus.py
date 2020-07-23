""" Testing Modbus Protocol using PyModbus
    Investing running Modbus as its own process on the Pi """

# Import Necessary Modules for Asycronous Communication
from twisted.internet import serialport, reactor
from twisted.internet.protocol import ClientFactory

# Import Necessary Modules for Syncronous Communication
from pymodbus.factory import ClientDecoder
from pymodbus.client.asynchronous.twisted import ModbusClientProtocol

# Import Propper Framer (RTU -- Page 36 of Manuel)
from pymodbus.transaction import ModbusRtuFramer as ModbusFramer


# Configure Client Logging
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Define Device Address
UNIT = 0x1

def run_sync_client():
    """ Main loop for Modbus communication """
    client = ModbusClient(method='rtu', port='/dev/ptyp0', timeout=1, baudrate=9600)
    client.connect()
