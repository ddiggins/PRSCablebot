import pytest
import sys
sys.path.append("..") # Adds higher directory to python modules path.
import SerialCommunication
import os, pty, serial

def test_start_serial():
    serial = SerialCommunication.start_serial()
    assert serial is not None

def test_send_command():
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
        ticket = send_command(None, '{"id" : "Motor1", "enabled" : "0"}')

def test_recieve_command():
    master, slave = pty.openpty()
    os.write(master, ('{"id" : "Motor1", "enabled" : "0"}').encode())

    s_name = os.ttyname(slave)
    ser = serial.Serial(s_name, 115200, timeout=1)
    assert SerialCommunication.receive_command(ser) == '{"id" : "Motor1", "enabled" : "0"}'