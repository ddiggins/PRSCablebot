import pytest
import sys
sys.path.append("..") # Adds higher directory to python modules path.
from logger import Logger
import app

# Initialize testing app
test_logger = app.unit_testing() # This initializes a logger called "logger"

def test_interpret_json():

    #Initialize Logger
    # logger = Logger(incoming_commands, outgoing_commands, lock, socketio, 'test_logger.txt', connector_queues)

    # Normal conditions
    json_message = '{"id" : "Sensor1", "enabled" : "1"}'
    test_logger.interpret_json(json_message)
    assert test_logger.data_dict == {"Sensor1" : {"id" : "Sensor1", "enabled" : "1"}}
    assert test_logger.data_dict["Sensor1"] == {"id" : "Sensor1", "enabled" : "1"}

    # "id" key doesn't exist in incoming message
    test_logger.data_dict = {} # Setting dict to empty for new tests
    json_message = '{"" : "Sensor1", "enabled" : "1"}' 
    test_logger.interpret_json(json_message)
    assert test_logger.data_dict is None

    # "id" key exists but there is no value
    test_logger.data_dict = {} # Setting dict to empty for new tests
    json_message = '{"id" : "", "enabled" : "1"}' 
    test_logger.interpret_json(json_message)
    assert test_logger.data_dict is None
    pass

def test_log_data():
    pass

def test_run_logger():
    pass

