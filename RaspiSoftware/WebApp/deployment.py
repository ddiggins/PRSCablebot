""" Deployment routine manager for automating robot control """
import time
import json
import SerialCommunication
from multiprocessing import Queue, Process, Pipe
from flask_socketio import SocketIO, emit, send


class Deployment:

    """ Manager for robot deployment.

        Reads a text file which describes a deployment and
        executes it.
        
        List of commands:

        enable sensors:
        ENABLE (sensors comma delimited)

        go to position:
        GO_TO (position in meters)
        
        go at speed:
        GO_AT_SPEED (speed in steps/ms)

        pause:
        PAUSE (time in s)

        take measurement:
        TAKE_MEASUREMENT
        """

    
    def __init__(self, serial, file):
        """ Create a deployment object and define
            possible commands to be executed """

        self.socketio = SocketIO(message_queue='redis://')
        self.serial = serial # pipe SERIAL_CHILD
        self.filename = file
        self.document = open(self.filename, "r")
        self.zero_position = 0
        self.position = 0

        self.speed = 0
        self.commands = {

            "ENABLE":self.enable_sensors,
            "DISABLE":self.disable_sensors,
            "GO_TO": self.go_to,
            "GO_AT_SPEED": self.set_speed,
            "PAUSE": self.pause,
            "TAKE_MEASUREMENT": self.take_measurement,
            "RESET_ENCODER": self.reset_encoder_zero
        }

    def interpret_line(self, line):
        """ Checks the command found in the line with the commands dictionary.
        Calls the appropriate function and passes in a list of arguments.
        """
        command = line.split()[0]
        func = self.commands.get(command)
        assert func is not None, "Invalid command"

        if len(line.split()) != 1:
            func(line.split()[1:])
            return
        func()

    def enable_sensors(self, sensors):
        print("Enabling Sensors %s" % sensors)
        for i in sensors:
            self.serial.send(('{"id" : "%s", "enabled" : "1"}' % i))
    
    def disable_sensors(self, sensors):
        print("Disabling Sensors %s" % sensors)
        for i in sensors:
            self.serial.send(('{"id" : "%s", "enabled" : "0"}' % i))

    def set_speed(self, speed):
        print("Setting speed to %s " % speed[0])
        self.serial.send('{"id":"Motor1", "mode":"2","target":"%s"}' % speed[0])

    def update_position(self, data):
        ''' format of encoder value data:
        (name, value, timestamp)
        '''
        data = json.loads(data)
        print("data:", data)
        print("ENCODER?", data[0])
        if data[0] == "encoder":
            self.position = data[1]
            print(self.position)


    def go_to(self, position):
        #TODO: make sure robot actually moves to location before next command using encoder values
        #from database
        position = float(position[0]) + float(self.zero_position[0])
        print("Going to %s meters" % position)
        steps = position * 2717 # Convert m to steps
        self.target = steps
        print(self.target)
        self.serial.send('{"id":"Motor1", "mode":"1","target":"%s"}' % steps)
        print("sent serial command")
        self.socketio.emit("testing deployment socket")

        # Wait until encoder position is what we want
        while 1:
            self.socketio.emit("testing deployment socket", namespace='/test')
            self.socketio.on_event('update table', self.update_position)
            if abs(self.position - steps) < 50:
                break
            time.sleep(.1)

    def pause(self, pause_time):
        seconds = float(pause_time[0])
        print("Sleeping for %i seconds" % seconds)
        time.sleep(seconds)

    def take_measurement(self):
        print("TAKING MEASUREMENT")

    def reset_encoder_zero(self, position):
        self.zero_position = position

    def run_deployer(self):
        for line in self.document:
            if line is not []:
                self.interpret_line(line)

def start_deployment(serial, file):
    deployer = Deployment(serial, file)
    deployer.run_deployer()



if __name__ == "__main__":

    SERIAL_CHILD, SERIAL_PARENT = Pipe()
    RECORD_QUEUE = Queue()
    COMMUNICATOR = Process(target=SerialCommunication.start_serial_communication,\
        args=(RECORD_QUEUE, SERIAL_CHILD))
    COMMUNICATOR.start()

    DEPLOYMENT = Deployment(SERIAL_PARENT, "deployment_test.txt")
    DEPLOYMENT.run()
    COMMUNICATOR.join()
    while not RECORD_QUEUE.empty():
        print(RECORD_QUEUE.get())
