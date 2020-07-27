""" Testing Modbus Protocol using PyModbus
    Investing running Modbus as its own process on the Pi
    https://pymodbus.readthedocs.io/en/latest/index.html """

# Import Necessary Modules for Asycronous Communication
# from twisted.internet import serialport, reactor
# from twisted.internet.protocol import ClientFactory
# from pymodbus.factory import ClientDecoder
# from pymodbus.client.asynchronous.twisted import ModbusClientProtocol

# Import Necessary Modules for Syncronous Communication
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

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
UNIT = 0x0

def run_sync_client():
    """ Main loop for Modbus communication """
    # Define client connection
    client = ModbusClient(method='rtu', port='/dev/tty0', timeout=1, baudrate=9600)
    client.connect()

    # Specify target device
    log.debug("Reading Coils")
    rr = client.read_coils(1, 1, unit=UNIT)
    log.debug(rr)

    # Close Client
    client.close()

if __name__ == "__main__":
    run_sync_client()