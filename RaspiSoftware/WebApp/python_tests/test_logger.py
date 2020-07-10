from multiprocessing import Process, Queue, Lock
import sys
import os
import threading

import pytest
sys.path.append("..") # Adds higher directory to python modules path.
from gevent import monkey
from logger import Logger
import app
import sqlConnector
from threading import Thread, Lock
from flask import Flask, render_template, url_for, redirect
from flask_socketio import SocketIO, emit, send
from forms import SerialSendForm
import SerialCommunication
import json
import logging
import logger
import sqlConnector
import datetime

monkey.patch_all()

def init_testing_app():
    ''' Creates a testing app so that logger can be instantiated. 
    '''
    app = Flask("test")

    # Suppresses terminal outputs of GET and POST. Only allows error messages.
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    # Secret key to use for cookies (Definitely not secure but secure enough)
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY

    # Initialize Socket.io
    socketio = SocketIO(app)

    # Lists to display incoming and outgoing commands
    incoming = []
    outgoing = []

    # A mutex to protect the incoming queue
    lock = Lock()

    # Queues for serial commands
    outgoing_commands = Queue()
    incoming_commands = Queue()

    # Queues for sql database connector
    lock_global = Lock()
    connector = sqlConnector.SQLConnector("sensorLogs", "sensorData", True, lock_global)
    request_queue_global = Queue()
    record_queue_global = Queue()
    answer_queue_global = Queue()
    connector_queues = [request_queue_global, record_queue_global, answer_queue_global, lock_global]

    connector = Process(target=connector.run_database_connector,\
        args=(request_queue_global, record_queue_global, answer_queue_global))
    connector.start()

    # Starts thread that runs serial communication.
    communicator = Process(target=SerialCommunication.run_communication,\
            args=(outgoing_commands, incoming_commands, lock_global))
    communicator.start()

    # Starts background task that continually checks for incoming messages.
    test_logger = logger.Logger(incoming_commands, outgoing_commands, lock_global, socketio, "testLog.txt", connector_queues)
    # socketio.start_background_task(test_logger.run_logger)
    loggerprocess = Process(target=test_logger.run_logger)
    loggerprocess.start()

    # Create thread that runs app through SocketIO
    socketprocess = Process(target=socketio.run, args=(app,), kwargs={"debug":False, "host":'0.0.0.0', "use_reloader":False})
    socketprocess.start()

    return test_logger, loggerprocess, connector, communicator, socketprocess, incoming_commands

def kill_testing_app(socketprocess, communicator, connector, loggerprocess):
    ''' Kills processes associated with the testing app.
    '''
    socketprocess.kill()
    communicator.kill()
    connector.kill()
    loggerprocess.kill()

def test_interpret_json():

    test_logger, loggerprocess, connector, communicator, socketprocess, incoming_commands = init_testing_app()

    # Normal conditions
    json_message = '{"id" : "Sensor1", "enabled" : "1"}'
    test_logger.interpret_json(json_message)
    assert test_logger.data_dict == {"Sensor1" : {"id" : "Sensor1", "enabled" : "1"}}
    assert test_logger.data_dict["Sensor1"] == {"id" : "Sensor1", "enabled" : "1"}

    # "id" key doesn't exist in incoming message
    test_logger.data_dict = {} # Setting dict to empty for new tests
    json_message = '{"" : "Sensor1", "enabled" : "1"}' 
    with pytest.raises(AssertionError):
        test_logger.interpret_json(json_message)

    # "id" key exists but there is no value
    test_logger.data_dict = {}
    json_message = '{"id" : "", "enabled" : "1"}'
    with pytest.raises(AssertionError):
        test_logger.interpret_json(json_message)    

    # invalid Json message
    test_logger.data_dict = {}
    json_message = '{"id", "enabled" : "1"}'
    with pytest.raises(ValueError):
        test_logger.interpret_json(json_message)    

    # Ends testing environment app
    kill_testing_app(socketprocess, communicator, connector, loggerprocess)

def test_log_data():
    test_logger, loggerprocess, connector, communicator, socketprocess, incoming_commands = init_testing_app()

    # Normal Conditions, should log file and write records to database
    data_dict = {"id" : "Sensor1", "enabled" : "1", "value" : "5"}
    test_logger.log_data(data_dict)
    test_log_file = open

    with open(test_logger.log_file_name) as test_log_file:
        for line in test_log_file:
            pass
        last_line = line

    # Search for starting bracket
    print("line: ", last_line)
    print("split line: ", last_line.split("{"))
    print(last_line.split("{")[1])
    assert last_line.split("{")[1] == '"id": "Sensor1", "enabled": "1", "value": "5"}\n'

    # Invalid data_dict - not an actual dict
    data_dict = {"Sensor1":{"id" : "Sensor1", "enabled" : "1"}}
    with pytest.raises(AssertionError):
        test_logger.log_data(data_dict)    
    kill_testing_app(socketprocess, communicator, connector, loggerprocess)

    test_log_file.close() 
