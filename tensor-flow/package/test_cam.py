from picamera import PiCamera
from time import sleep

with PiCamera() as cam:
    cam.start_preview()
    cam.led = True
    sleep(20)
    cam.stop_preview()
    cam.led = False
    cam.close()
    
