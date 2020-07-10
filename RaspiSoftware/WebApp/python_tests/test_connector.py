""" Tests for the mySQL connector interface """
import pytest
import datetime
from multiprocessing import Process, Queue, Lock
import time
import sys
sys.path.append("..") # Adds higher directory to python modules path.
import sqlConnector


def test_connector():
    """ Test the creation and initialization of the connector class """
    lock_global = Lock()
    connector = sqlConnector.SQLConnector("sensorLogs", "testData", True, lock_global)
    assert connector is not None


def test_add_data():
    """ Test adding data to the database and verifying that it is added """
    # Normal Conditions
    lock_global = Lock()
    connector = sqlConnector.SQLConnector("sensorLogs", "testData", True, lock_global)
    res = connector.add_data('1000-01-01 00:00:00.000', "testName", "testValue")
    assert res == 1 # rows added
    res = connector.add_data('1000-01-01 00:00:00.000', "testName", "testValue")
    assert res == 1

    # Bad things that should throw error
    with pytest.raises(TypeError):
        # wrong number of args
        res = connector.add_data('1000-01-01 00:00:00.000', "testName", "testValue", "Other stuff")
    with pytest.raises(AssertionError):
        # number instead of string
        res = connector.add_data('1000-01-01 00:00:00.000', "testName", 5)
    with pytest.raises(ValueError):
        res = connector.add_data('-1', "testName", "testValue") # Malformatted Date
    with pytest.raises(AssertionError):
        # Input too long
        res = connector.add_data('1000-01-01 00:00:00.000', "testNamesdfgjklkjhgffrkdsljhfie;owjofijewoa;fnoeiwa;nfcoiewnafoicmaweofnoi;ewanfcoiweanmoficnwaeoincoewinafciewoanfdoieawnfioewnfoiweanifoanwlfkwnlkfeanlewalntestNamesdfgjklkjhgffrkdsljhfie;owjofijewoa;fnoeiwa;nfcoiewnafoicmaweofnoi;ewanfcoiweanmoficnwaeoincoewinafciewoanfdoieawnfioewnfoiweanifoanwlfkwnlkfeanlewalntestNamesdfgjklkjhgffrkdsljhfie;owjofijewoa;fnoeiwa;nfcoiewnafoicmaweofnoi;ewanfcoiweanmoficnwaeoincoewinafciewoanfdoieawnfioewnfoiweanifoanwlfkwnlkfeanlewalntestNamesdfgjklkjhgffrkdsljhfie;owjofijewoa;fnoeiwa;nfcoiewnafoicmaweofnoi;ewanfcoiweanmoficnwaeoincoewinafciewoanfdoieawnfioewnfoiweanifoanwlfkwnlkfeanlewalntestNamesdfgjklkjhgffrkdsljhfie;owjofijewoa;fnoeiwa;nfcoiewnafoicmaweofnoi;ewanfcoiweanmoficnwaeoincoewinafciewoanfdoieawnfioewnfoiweanifoanwlfkwnlkfeanlewalntestNamesdfgjklkjhgffrkdsljhfie;owjofijewoa;fnoeiwa;nfcoiewnafoicmaweofnoi;ewanfcoiweanmoficnwaeoincoewinafciewoanfdoieawnfioewnfoiweanifoanwlfkwnlkfeanlewaln", "testValue")


def test_query_sensor():
    """ Test queries without multiprocessing """
    lock_global = Lock()
    connector = sqlConnector.SQLConnector("sensorLogs", "testData", True, lock_global)
    connector.add_data('2000-01-01 00:00:01.000', "testName", "testValue")

    # Test query of a single record
    res = connector.query_sensor("testName", 1, "timestamp")
    assert res == (1, datetime.datetime(2000, 1, 1, 0, 0, 1), "testName", "testValue")

    # Test multiple query sorted by timestamp
    connector.add_data('2000-01-01 00:00:02.000', "testName", "testValue")
    res = connector.query_sensor("testName", 2, "timestamp")
    assert res == [(1, datetime.datetime(2000, 1, 1, 0, 0, 1), "testName", "testValue"), (2, datetime.datetime(2000, 1, 1, 0, 0, 2), "testName", "testValue")]


def test_process_request():
    """ Test multiprocessing queries and synchronization.
    NOTE: Because the communication is queue based there is no guarantee that
    records will be fully up to date when they are pulled. This is an intentional
    decision as it is not usually necissary to have to-the-milisecond information
    but makes testing difficult. """

    request_queue_global = Queue()
    record_queue_global = Queue()
    answer_queue_global = Queue()
    lock_global = Lock()

    connector = sqlConnector.SQLConnector("sensorLogs", "testData", True, lock_global)

    connector = Process(target=connector.run_database_connector,\
            args=(request_queue_global, record_queue_global, answer_queue_global))
    connector.start()

    # Adding records
    sqlConnector.add_record(('2000-01-01 00:00:01.000', "testName", "testValue"), record_queue_global, lock_global)
    sqlConnector.add_record(('2000-01-01 00:00:02.000', "testName", "testValue"), record_queue_global, lock_global)

    while not record_queue_global.empty(): time.sleep(0.01)
    time.sleep(.5) # Let the queue empty completely

    print("about to get record")
    record = sqlConnector.request_record(('testName', 2, 'timestamp'), request_queue_global, answer_queue_global, lock_global)
    print("got record")
    print("record is" + str(record))
    connector.kill()
    assert record == [(1, datetime.datetime(2000, 1, 1, 0, 0, 1), "testName", "testValue"), (2, datetime.datetime(2000, 1, 1, 0, 0, 2), "testName", "testValue")]
