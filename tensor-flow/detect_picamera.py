# python3
#
# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Example using TF Lite to detect objects with the Raspberry Pi camera."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import io
import re
import os
import time
import datetime
import requests
import threading

from annotation import Annotator

import numpy as np
import picamera

from PIL import Image
from tflite_runtime.interpreter import Interpreter
from dotenv import load_dotenv
from sig import button_interrupt, button_press

load_dotenv()

# ================================ Detection Functions ================================
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

WINDOW_X = 1920//4
WINDOW_Y = 0

def load_labels(path):
  """Loads the labels file. Supports files with or without index numbers."""
  with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    labels = {}
    for row_number, content in enumerate(lines):
      pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)
      if len(pair) == 2 and pair[0].strip().isdigit():
        labels[int(pair[0])] = pair[1].strip()
      else:
        labels[row_number] = pair[0].strip()
  return labels


def set_input_tensor(interpreter, image):
  """Sets the input tensor."""
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image


def get_output_tensor(interpreter, index):
  """Returns the output tensor at the given index."""
  output_details = interpreter.get_output_details()[index]
  tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
  return tensor


def detect_objects(interpreter, image, threshold):
  """Returns a list of detection results, each a dictionary of object info."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()

  # Get all output details
  boxes = get_output_tensor(interpreter, 0)
  classes = get_output_tensor(interpreter, 1)
  scores = get_output_tensor(interpreter, 2)
  count = int(get_output_tensor(interpreter, 3))

  results = []
  for i in range(count):
    if scores[i] >= threshold and classes[i] == 0:
      result = {
          'bounding_box': boxes[i],
          'class_id': classes[i],
          'score': scores[i]
      }
      results.append(result)
  return results


def annotate_objects(annotator, results, labels):
  """Draws the bounding box and label for each object in the results."""
  for obj in results:
    # Convert the bounding box figures from relative coordinates
    # to absolute coordinates based on the original resolution
    ymin, xmin, ymax, xmax = obj['bounding_box']
    xmin = int(xmin * CAMERA_WIDTH )
    xmax = int(xmax * CAMERA_WIDTH )
    ymin = int(ymin * CAMERA_HEIGHT)
    ymax = int(ymax * CAMERA_HEIGHT)

    # Overlay the box, label, and score on the camera preview
    annotator.bounding_box([xmin, ymin, xmax, ymax])
    annotator.text([xmin, ymin],
                   '%s\n%.2f' % (labels[obj['class_id']], obj['score']))

# ================================ Data Handling Class ================================
SERVER_IP = os.environ["SERVER_IP"]
ROUTE = f"https://{SERVER_IP}/admin/pi"
ROUTE = f"https://yncgym.ml/admin/pi"

class Data(object):
  """Object to encapsulate data sending/preprocessing"""
  def __init__(self):
    self.data = dict()
    self.count = 0
    self.results = []
    self.flag = True

  def process_result(self):
    """Processing routine called everytime image data comes in"""
    if self.count < 5:
      self.count += 1
      self.data[f'img{self.count}'] = len(self.results)
      print(self.data)
    else:
      self.count = 0
      self.data['mode'] = sorted([value for value in self.data.values()])[2]
      self.data['timestamp'] = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
      print(self.data)
      self.send_data(ROUTE)

  def send_data(self, endpoint):
    """Send data to the server"""
    try:
      r = requests.post(endpoint,
                        json=self.data,
                        verify=True,
                        timeout=2)
      r.raise_for_status()
    except Exception as e:
      print("Could not send data\n")
      print(e)
    finally:
      self.data.clear()
      time.sleep(1)

  def timer_thread(self):
    """Signal post event to run.py"""
    time.sleep(2)
    while self.flag:
      self.process_result()
      time.sleep(1)


# ================================ Camera ======================================
def start_background(interpreter, threshold):
  """Start image detection in the background"""
  _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']
  with picamera.PiCamera(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30) as camera:
    camera.vflip = True
    D = Data()
    stream = io.BytesIO()
    while button_press.wait():
      try:
          stream.truncate()
          stream.seek(0)
          camera.capture(stream, format='jpeg', resize=(input_width, input_height))
          image = Image.open(stream)
          D.results = detect_objects(interpreter, image, threshold)
          D.process_result()
          time.sleep(1)

      except KeyboardInterrupt:
        break

    print("Exitting")

def watch_background(input_width, input_height, interpreter, labels, threshold):
  """Start image detection with preview"""
  with picamera.PiCamera(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30) as camera:
    camera.vflip = True
    camera.led = True
    D = Data()
    t = threading.Thread(target=D.timer_thread)
    camera.start_preview() # fullscreen=False, window=(WINDOW_X,WINDOW_Y,CAMERA_WIDTH,CAMERA_HEIGHT))
    t.start()
    time.sleep(2)
    stream = io.BytesIO()
    annotator = Annotator(camera, "green")
    while True():
      try:
          for _ in camera.capture_continuous(stream, format='jpeg',
                                            resize=(input_width, input_height),
                                            use_video_port=True):
            stream.seek(0)
            image = Image.open(stream).convert('RGB')
            #.resize((input_width, input_height), Image.NEAREST)#Image.ANTIALIAS)
            
            start_time = time.monotonic()
            D.results = detect_objects(interpreter, image, threshold)
            elapsed_ms = (time.monotonic() - start_time) * 1000

            annotator.clear()
            annotate_objects(annotator, D.results, labels)
            annotator.text([5, 0], '%.1fms' % (elapsed_ms))
            annotator.text([540, 0], f"Person count: {len(D.results)}")
            annotator.update()
            stream.seek(0)
      except KeyboardInterrupt:
        break
      finally:
        D.flag = False
        t.join()
        camera.stop_preview()
        print("Quitting\n")


# ================================ CLI Args =====================================
def parse_cli_args():
  """Commnad line options parser"""
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
    '--model',
    help='File path of .tflite file.',
    required=False,
    default="detect.tflite")
  parser.add_argument(
    '--labels',
    help='File path of labels file.',
    required=False,
    default="coco_labels.txt")
  parser.add_argument(
    '--threshold',
    help='Score threshold for detected objects.',
    required=False,
    type=float,
    default=0.6)
  parser.add_argument(
    '--watch', help='1 or 0',
    required=False,
    type=bool,
    default=0)
  return parser.parse_args()

# ================================ Main Function ================================
@button_interrupt
def main():
  args = parse_cli_args()

  # Configuration
  labels = load_labels(args.labels)
  interpreter = Interpreter(args.model)
  interpreter.allocate_tensors()
  _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']

  if args.watch:
    watch_background(input_width, input_height, interpreter, labels, args.threshold)
  else:
    start_background(interpreter, args.threshold)

if __name__ == '__main__':
  main()
