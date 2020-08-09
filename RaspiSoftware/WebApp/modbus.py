""" Class for communication with AqualTROLL using Modbus protocol
    using minimal pymodbus"""

import minimalmodbus
import serial
import time
import struct
import logging
from datetime import datetime
from multiprocessing import Queue, Process
import numpy as np
import pandas as pd


FORMAT = ('%(asctime)-15s %(threadName)-15s'
    ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.ERROR)

UNIT = 0x01

class Modbus:
    """ Object to handle modbus communication with an InSitu AquaTroll"""

    def __init__(self, record_queue):
        """Creates Modbus object, defines client, log, and empty sensor list"""

        self.instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # port name, slave address (in decimal)
        self.instrument.serial.parity = serial.PARITY_EVEN
    
        # self.log = log
        self.sensors = []
        self.record_queue = record_queue

        # Creates appendixes
        self.AppendixB = self.csv_to_dictionary('AppendixB_paramNumsAndLocations.csv')
        self.AppendixC = self.csv_to_dictionary('AppendixC_unitIDs.csv')

        self.instrument.serial.timeout = 2
        self.wake_up()
        self.init_sensor_discovery()

    def wake_up(self):
        """Creates connection with the AquaTROLL and follow wakeup procedure.
        This involves sending a wake-up command and reading the sensors"""
        try:
            self.instrument.read_register(0) # Wake up sensor
        except:
            time.sleep(1)

        return True

    def collect_data(self):
        """Given the list of sensors (self.sensors) collect all sensor data
        and return it as a list of dictionaries"""
        data = []
        self.wake_up()
        for sensor in self.sensors:
            measurement = self.read_sensor(sensor['address'])
            data_point = {'sensor':"" + sensor['param'] + " " + sensor['unit_abbr'],
                          'value':measurement['value'],
                          'timestamp':datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}
            data.append(data_point)
            self.record_queue.put((data_point['timestamp'],\
                    str(data_point['sensor']), str(data_point['value'])))
        
        return data

    def read_sensor(self, address):
        """Reads the registers from a sensor given the sensor address
         A sensor consists of 7 registers which encode the data and other parameters
         Returns: Dictionary which encodes data into five values: value, qualityId, unitId, paramId, sentinel"""

        data = {}
        request = self.instrument.read_registers(address, 7)


        value = np.array([(request[0] << 16) + request[1]], dtype=np.uint32)
        value = value.view(np.single).item(0)
        quality_id = request[2]
        unit_id = request[3]
        param_id = request[4]
        sentinel = np.array([(request[5] << 16) + request[6]], dtype=np.uint32)
        sentinel = sentinel.view(np.single).item(0)

        data = {'value':value, 'quality_id':quality_id, 'unit_id':unit_id, 'param_id':param_id, 'sentinel':sentinel}

        #TODO: Decode information into data
        #TODO: Throw error is data quality is low or corrupted
        #TODO: Return measured value

        # decoded = OrderedDict([
        #     ('value', decoder.decode_32bit_float()),
        #     ('quality_id', decoder.decode_16bit_uint()),
        #     ('unit_id', decoder.decode_16bit_float()),
        #     ('param_id', decoder.decode_16bit_uint()),
        #     ('sentinel', decoder.decode_32bit_float())
        # ])

        return data


    def read_register(self, address, count):
        """Reads a register number and returns a list of bits"""
        request = self.instrument.read_registers(address, count)
        return request


    def init_sensor_discovery(self):
        """Reads a 14 register block that starts with 6984 that triggers the sonde to scan
        its sensor ports and update its sensor map. There are a total of 219 parameter IDs.
        A total of 59 parameters exist.

        Returns: list of ids that have enabled sensors
        """
        res = self.instrument.read_registers(6983, 14)
        result = 0
        for i in range(13, 0):
            result += res[i] << 16*i

        sensors = []
        for i in res:
            for j in range(16):
                sensors.append(self.get_bit(i, j))

        enabled = [self.AppendixB[i+1] for i in range(224) if sensors[i]]

        self.sensors = enabled
        print(enabled)

        return enabled


    def get_bit(self, num, n):
        return (num >> n) & 1


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


    def get_param_id_properties(self, param_id, prop_requested="all"):
        """Returns properties of a sensor"""
        if prop_requested == "all":
            properties = self.AppendixB.get(param_id)
        return properties


    def get_unit_id_properties(self, unit_id):
        properties = self.AppendixC.get(unit_id)
        return properties

    def check_error(self, res):
        if isinstance(res, Exception):
            raise res
    
    def csv_to_dictionary(self, csvFile):
        '''
        Takes a csv file and converts it into a dictionary with the following format:
        {1: {'Parameter Name': 'Temperature', 'Holding Register Number': 5451, 'Holding Register Address': 5450, 'Default Unit ID': 1, 'Default Unit Abbreviation': '°C'}, 
        2: {'Parameter Name': 'Pressure', 'Holding Register Number': 5458, 'Holding Register Address': 5457, 'Default Unit ID': 17, 'Default Unit Abbreviation': 'PSI'},
        ...
        }'''
        df = pd.read_csv(csvFile)
        df = df.set_index('ID')
        data_dict = df.to_dict('index')

        return data_dict


def start_modbus(record_queue):

    modbus = Modbus(recrd_queue, log)


if __name__ == "__main__":
    modbus = Modbus(log)
    # data = modbus.read_sensor(5450)
    modbus.collect_data()
    log.debug(data)
    log.debug(modbus.sensors)
