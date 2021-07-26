import io

from threading import Thread
from picamera import PiCamera
from PIL import Image
from time import sleep, monotonic

from data import Data
from detector import Detector
from sig import button_press, button_interrupt
from annotation import Annotator

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

@button_interrupt
def start_background(detector:Detector):
    """Start image detection in the background"""
    data = Data()
    with PiCamera(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30) as camera:
        camera.vflip = True
        stream = io.BytesIO()
        while button_press.wait():
            try:
                stream.truncate()
                stream.seek(0)
                camera.capture(stream, format='jpeg', resize=(detector.input_width, detector.input_height))
                image = Image.open(stream)
                data.results = detector.detect_objects(image)
                data.process_result()
                sleep(1)

            except KeyboardInterrupt:
                break

        print("Exitting")


@button_interrupt
def watch_background(detector:Detector):
    """Start image detection with preview"""
    data = Data()
    t = Thread(target=data.timer_thread)
    with PiCamera(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30) as camera:
        camera.vflip = True
        camera.led = True
        camera.start_preview()  # fullscreen=False, window=(WINDOW_X,WINDOW_Y,CAMERA_WIDTH,CAMERA_HEIGHT))
        sleep(2)
        t.start()
        stream = io.BytesIO()
        annotator = Annotator(camera, "green")
        while True():
            try:
                for _ in camera.capture_continuous(stream, format='jpeg',
                                                   resize=(detector.input_width, detector.input_height),
                                                   use_video_port=True):
                    stream.seek(0)
                    image = Image.open(stream).convert('RGB')
                    # .resize((input_width, input_height), Image.NEAREST)#Image.ANTIALIAS)

                    start_time = monotonic()
                    data.results = detector.detect_objects(image)
                    elapsed_ms = (monotonic() - start_time) * 1000

                    annotator.clear()
                    detector.annotate_objects(annotator, data.results, detector.labels)
                    annotator.text([5, 0], '%.1fms' % (elapsed_ms))
                    annotator.text([540, 0], f"Person count: {len(data.results)}")
                    annotator.update()
                    stream.seek(0)
            except KeyboardInterrupt:
                break
            finally:
                data.flag = False
                t.join()
                camera.stop_preview()
                print("Quitting\n")