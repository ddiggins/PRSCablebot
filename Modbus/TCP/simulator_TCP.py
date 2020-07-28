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

# # Build Payload
# builder = BinaryPayloadBuilder(byteorder=Endian.Big)
# builder.add_32bit_float(12.34)
# builder.add_16bit_uint(0)
# builder.add_16bit_float(1)
# builder.add_16bit_uint(1)
# builder.add_32bit_float(0.0)
# payload = builder.build()
# print(payload)

class Sensor:
    """ A sensor object which carries the valuies for one sensor """
    def __init__(self, value, qualityId, unitId, paramId, sentinel):
        """ Copy over values """
        self.value, self.qualityId, self.unitId, self.paramId, self.sentinel = value, qualityId, unitId, paramId, sentinel


def create_space(builder, space):
    builder.add_bits([0]*space)


def blank_sensor(paramId):
    return Sensor(0, 0, 0, paramId, 0)


def create_enabled_builder(builder, devices):
    """ Adds pins for which sensors are enabled """
    bits = []

    # Create bit list
    for i in range(224):
        if i in devices:
            bits.append(1)
        else:
            bits.append(0)

    builder.add_bits(bits)


def add_sensor(builder, sensor):
    """ Adds a single sensor to the builder """
    builder.add_32bit_float(sensor.value)
    builder.add_16bit_uint(sensor.qualityId)
    builder.add_16bit_float(sensor.unitId)
    builder.add_16bit_uint(sensor.paramId)
    builder.add_32bit_float(sensor.sentinel)


def add_sensors(builder, sensors):
    sensor_numbers = []
    for sensor in sensors:
        sensor_numbers.append(sensor.paramId)
    log.debug(sensor_numbers)


    for i in range(1, 60):
        if i in sensor_numbers:
            position = sensor_numbers.index(i)
            log.debug(position)
            add_sensor(builder, sensors[position])
        else:
            add_sensor(builder, blank_sensor(i))

    return sensor_numbers


# Sensors
temp_sensor = Sensor(17.3, 0, 1, 1, 0.0)
depth_sensor = Sensor(15.4, 0, 38, 3, 0.0)
ph_sensor = Sensor(7.4, 0, 145, 17, 0.0)
do_sensor = Sensor(14.35, 0, 117, 20, 0.0)

Builder = BinaryPayloadBuilder(byteorder=Endian.Big)

numbers = add_sensors(Builder, [temp_sensor])
create_space(Builder, 1121*16)
# create_space(Builder, 1)
create_enabled_builder(Builder, numbers)




block = ModbusSequentialDataBlock(5451, Builder.to_registers())
# block = ModbusSequentialDataBlock(6984, Builder.to_registers())

store = ModbusSlaveContext(
    di=block,
    co=block,
    hr=block,
    ir=block)
context = ModbusServerContext(slaves=store, single=True)
StartTcpServer(context, framer=ModbusRtuFramer, address=("0.0.0.0", 5020))
