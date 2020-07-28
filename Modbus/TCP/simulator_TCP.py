""" Creating Modbus Emulator
    https://pymodbus.readthedocs.io/en/latest/index.html """

# Import PyModBus Packages for server
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.transaction import ModbusRtuFramer

# Import Payload
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder

# Import and Configure Logging
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Build Payload
builder = BinaryPayloadBuilder(byteorder=Endian.Big)
builder.add_32bit_float(12.34)
builder.add_16bit_uint(0)
builder.add_16bit_float(1)
builder.add_16bit_uint(1)
builder.add_32bit_float(0.0)
payload = builder.build()
print(payload)

builder2 = BinaryPayloadBuilder(byteorder=Endian.Big)
builder2.add_16bit_uint(0)
builder2.add_16bit_uint(0)
builder2.add_16bit_uint(0)
builder2.add_16bit_uint(0)
builder2.add_16bit_uint(1)
builder2.add_16bit_uint(0)
builder2.add_16bit_uint(0)
builder2.add_16bit_uint(0)
builder2.add_16bit_uint(0)
builder2.add_16bit_uint(0)
builder2.add_16bit_uint(0)
builder2.add_16bit_uint(0)
builder2.add_16bit_uint(0)
builder2.add_16bit_uint(0)

# block = ModbusSequentialDataBlock(0x00, [1]*0x21) # binary
block = ModbusSequentialDataBlock(1, builder.to_registers())
parameterIdMap = ModbusSequentialDataBlock(6985, builder2.to_registers())
store = ModbusSlaveContext(
    di=block,
    co=block,
    hr=parameterIdMap,
    ir=block)
context = ModbusServerContext(slaves=store, single=True)
StartTcpServer(context, framer=ModbusRtuFramer, address=("0.0.0.0", 5020))
