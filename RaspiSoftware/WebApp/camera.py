""" Process to take images on the Pi at set intervals and save them to disk and database """

import time
from picamera import PiCamera
import datetime
from multiprocessing import Queue, Process


class Camera:
    """ A camera object to handle PiCamera settings """

    def __init__(self, resolution, interval, image_folder_path, record_queue, add_timestamp=True):

        """ Initialize a camera object with given settings """

        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = 15 # Required to set high resolution but not used
        self.add_timestamp = add_timestamp
        self.interval = interval # Amount of seconds between images
        self.camera.annotate_text_size = 50
        self.image_folder_path = image_folder_path
        self.record_queue = record_queue

    def take_image(self):
        """ Take a single image and save it with a unique name to the given folder """

        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        # print("ABOUT TO START PREVIEW")
        self.camera.start_preview()
        self.camera.annotate_text = timestamp + " UTC"
        time.sleep(2)
        image_name = self.image_folder_path + "/image" + str(timestamp) + ".jpg"
        # print("ABOUT TO CAPTURE IMAGE")
        self.camera.capture(image_name, quality=10)
        print("IMAGE CAPTURED")
        self.camera.stop_preview()
        print("PREVIEW ENDED")
        return timestamp, image_name

    def run_camera(self):
        """ Run the camera at the given update rate and put names into the queue """
        last_time = 0
        while 1:
            if time.time() - last_time > self.interval:
                last_time = time.time()
                print(last_time)
                timestamp, image_name = self.take_image()
                self.record_queue.put((timestamp, "Camera", image_name))
                print("ADDED TO QUEUE")
            time.sleep(0.01)

def start_camera(resolution, interval, image_folder_path, record_queue):
    print('running camera')
    camera = Camera(resolution, interval, image_folder_path, record_queue)
    camera.run_camera()



if __name__ == "__main__":
    QUEUE = Queue()
    # CAMERA = Camera(((2592, 1944)), 10, "Images", QUEUE)
    # # CAMERA.take_image()
    # CAMERA.run_camera()

    CAMERA_PROCESS = Process(target=start_camera, args=((2592, 1944), 10, "Images", QUEUE))
    CAMERA_PROCESS.start()
