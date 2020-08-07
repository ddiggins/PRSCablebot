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
import logging
from datetime import datetime
from table_extractor import csv_to_dictionary


FORMAT = ('%(asctime)-15s %(threadName)-15s'
    ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.ERROR)

UNIT = 0x0

class Modbus:

    def __init__(self, log):
        """Creates Modbus object, defines client, log, and empty sensor list"""
        
        self.client = ModbusClient('localhost', port=5020, framer=ModbusFramer)
        self.log = log
        self.sensors = []
        
        # Creates appendixes
        self.AppendixB = csv_to_dictionary('AppendixB_paramNumsAndLocations.csv')
        self.AppendixC = csv_to_dictionary('AppendixC_unitIDs.csv')
        
        self.begin_comms()
         

    def begin_comms(self):
        """Creates coonnection with the AquaTROLL and follow wakeup procedure.
        This involves sending a wake-up command and reading the sensors"""
        
        self.client.connect()
        #TODO: Insert wakeup command
        self.sensors = self.init_sensor_discovery()
        return True


    def collect_data(self):
        """Given the list of sensors (self.sensors) collect all sensor data
        and return it as a list of dictionaries"""
        data = []
        
        for sensor in self.sensors:
            measurement = self.read_sensor(sensor['address'])
            data_point = {'sensor':"" + self.AppendixB[measurement['param_id']]['param'] + " " + self.AppendixB[measurement['param_id']]['unit_abbr'],
                          'value':measurement['value'],
                          'timestamp':datetime.now().isoformat()}
            data.append(data_point)
        return data
            
        

    def read_sensor(self, address):
        """Reads the registers from a sensor given the sensor address
         A sensor consists of 7 registers which encode the data and other parameters
         Returns: Dictionary which encodes data into five values: value, qualityId, unitId, paramId, sentinel"""

        data = {}
        rr = self.client.read_holding_registers(address, 7, unit=UNIT)
        decoder = BinaryPayloadDecoder.fromRegisters(rr.registers, byteorder=Endian.Big)
        decoded = OrderedDict([
            ('value', decoder.decode_32bit_float()),
            ('quality_id', decoder.decode_16bit_uint()),
            ('unit_id', decoder.decode_16bit_float()),
            ('param_id', decoder.decode_16bit_uint()),
            ('sentinel', decoder.decode_32bit_float())
        ])
        
        for name, value in iteritems(decoded):
            data[name] = value
            # self.log.debug(str(name) + str(value))
        
        return data


    def read_register(self, address, count):
        """Reads a register number and returns a list of bits"""

        rr = self.client.read_holding_registers(address, count, unit=UNIT)
        decoder = BinaryPayloadDecoder.fromRegisters(rr.registers, byteorder=Endian.Big)
        res = []
        
        for i in range(count*2):
            ret = decoder.decode_bits()
            res.extend(ret)
        # self.log.debug(res)
        
        return res


    def init_sensor_discovery(self):
        """Reads a 14 register block that starts with 6984 that triggers the sonde to scan 
        its sensor ports and update its sensor map. There are a total of 219 parameter IDs. 
        A total of 59 parameters exist.

        Returns: list of ids that have enabled sensors
        """   
        res = self.read_register(6983,14) # 6984-1 not sure if correct
        enabled = []

        enabled = [self.AppendixB[i] for i in range(224) if res[i]]
        # self.log.debug(enabled)

        return enabled


    def get_registers_list(self):
        """ Returns a list of register numbers of enabled sensors given 
        a list of enabled sensor ids.
        """
        enabled_id_list = self.init_sensor_discovery()
        enabled_registers = []

        for param_id in enabled_id_list:
            param_register = (int(param_id)-1)*7+5451
            enabled_registers.append(param_register)

        return enabled_registers
    

    def get_param_id_properties(self, param_id, prop_requested = "all"):
        """Returns property 
        """
        if prop_requested == "all":
            properties = self.AppendixB.get(param_id)
            
        return properties


    def get_unit_id_properties(self, unit_id):
        properties = self.AppendixC.get(unit_id)
        return properties

def start_modbus():
    modbus = Modbus(log)

if __name__ == "__main__":
    modbus = Modbus(log)
    data = modbus.read_sensor(5450)
    modbus.collect_data()
    log.debug(data)
    log.debug(modbus.sensors)
