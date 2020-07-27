""" Class for communication with AqualTROLL using Modbus protocol
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


UNIT = 0x0

class Modbus:

    def __init__(self, log):
        """Creates Modbus object
        Connects to device using Modbus serial
        Instaniates logger"""
        # Connect
        self.client = ModbusClient('localhost', port=5020, framer=ModbusFramer)
        self.client.connect()
        self.log = log

        

    def read_sensor(self, address):
        """Reads the registers from a sensor given the sensor address
         A sensor consists of 7 registers which encode the data and other parameters
         Returns: Dictionary which encodes data into five values: value, qualityId, unitId, paramId, sentinel"""

        data = {}
        rr = self.client.read_holding_registers(address, 7, unit=UNIT)

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
            data[name] = value
            self.log.debug(str(name) + str(value))
        return data

    def read_register(self, address, count):
        """ Reads a register number and returns a list of bits"""

        rr = self.client.read_holding_registers(address, count, unit=UNIT)
        decoder = BinaryPayloadDecoder.fromRegisters(rr.registers, byteorder=Endian.Big)
        res = []
        for i in range(count*2):
            ret = decoder.decode_bits()
            res.extend(ret)
            self.log.debug(res)
        return res

    def init_sensor_discovery(self):
        '''
        Reads a 14 register block that starts with 6984 that triggers the sonde to scan 
        its sensor ports and update its sensor map. There are a total of 219 parameter IDs. 
        A total of 59 parameters exist.
        Returns: list of ids that have enabled sensors
        '''   
        res = self.read_register(6984,14)
        enabled = []

        enabled = [i for i in range(224) if res[i]]
        self.log.debug(enabled)
        
        return enabled

    def get_registers_list(self):
        '''
        Returns a list of registers of enabled sensors given a list of enabled sensor ids.
        '''
        enabled_id_list = self.init_sensor_discovery()
        enabled_registers = []

        for param_id in enabled_id_list:
            enabled_registers.extend((param_id-1)*7+5451)

        return enabled_registers        

if __name__ == "__main__":
    modbus = Modbus(log)
    data = modbus.init_sensor_discovery()
    log.debug(data)
