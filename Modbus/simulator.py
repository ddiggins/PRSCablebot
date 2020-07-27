""" Creating Modbus Emulator
    https://pymodbus.readthedocs.io/en/latest/index.html """

# Import PyModBus Packages for server
from pymodbus.server.asynchronous import StartSerialServer
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.transaction import ModbusRtuFramer

import logging

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)


store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [17]*100),
    co=ModbusSequentialDataBlock(0, [17]*100),
    hr=ModbusSequentialDataBlock(0, [17]*100),
    ir=ModbusSequentialDataBlock(0, [17]*100))
context = ModbusServerContext(slaves=store, single=True)
StartSerialServer(context, framer=ModbusRtuFramer, port='/dev/tty0')
