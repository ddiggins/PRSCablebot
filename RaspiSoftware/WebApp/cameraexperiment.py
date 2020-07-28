from multiprocessing import Process
import picamera
import time

def preview():
    with picamera.PiCamera() as cam:
        print("STARTING PREVIEW")
        cam.start_preview()
        print("PREVIEW STARTED")
        time.sleep(3)

p = Process(target=preview)
p.start()
time.sleep(5)