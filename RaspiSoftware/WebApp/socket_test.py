""" Deployment routine manager for automating robot control """
import time
import json
import SerialCommunication
from multiprocessing import Queue, Process, Pipe
from flask_socketio import SocketIO, emit, send


class Deployment:
    
    def __init__(self):
        """ Create a deployment object and define
            possible commands to be executed """

        self.socketio = SocketIO(message_queue='redis://')

    def update_position(self, data):
        print("updating position")

    def testing(self):
        self.socketio.emit("testing deployment socket", namespace='/test')
        self.socketio.on_event('update table', self.update_position)

        
def start_deployment(serial, file):
    deployer = Deployment()
    deployer.testing()



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
