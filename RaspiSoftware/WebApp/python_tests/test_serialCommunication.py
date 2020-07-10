import sys, os, pty, serial
import pytest
import SerialCommunication
sys.path.append("..") # Adds higher directory to python modules path.


def test_start_serial():
    """ Test the serial inizalization """
    ser = SerialCommunication.start_serial()
    assert ser is not None


def test_send_command():
    """ Test the serial send command """
    ser = SerialCommunication.start_serial()

    # Correct Statement
    ticket = SerialCommunication.send_command(ser, '{"id" : "Motor1", "enabled" : "0"}')
    assert ticket == 1

    # Corrupt Command
    # NOTE: send_command() does not process command and will send any statement
    ticket = SerialCommunication.send_command(ser, 'dsfvx{cvsddg#@sdflkj$b32r87)dfdgb')
    assert ticket == 1

    # Corrupt Serial
    with pytest.raises(Exception):
        ticket = SerialCommunication.send_command(None, '{"id" : "Motor1", "enabled" : "0"}')


def test_recieve_command():
    """ Test the serial recieve command """

    # Generate virtual serial
    rx, tx = pty.openpty()
    tx_name = os.ttyname(tx)
    ser = serial.Serial(tx_name, 115200, timeout=1)
    os.write(rx, ('{"id" : "Motor1", "enabled" : "0"}').encode())

    # Correct Statement
    assert SerialCommunication.receive_command(ser) == '{"id" : "Motor1", "enabled" : "0"}'
