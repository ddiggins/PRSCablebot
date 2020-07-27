""" Creating Modbus Emulator
    https://pymodbus.readthedocs.io/en/latest/index.html """

# Import PyModBus Packages for server
from pymodbus.server.asynchronous import StartSerialServer
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.transaction import ModbusRtuFramer

# Import and Configure Logging
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)


block = ModbusSequentialDataBlock(0x00, [0]*0xfe)

store = ModbusSlaveContext(
    di=block,
    co=block,
    hr=block,
    ir=block)
context = ModbusServerContext(slaves=store, single=True)
StartSerialServer(context, framer=ModbusRtuFramer, port='/dev/tty0')
