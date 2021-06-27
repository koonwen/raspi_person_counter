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
import time
import datetime
import requests
import threading

from annotation import Annotator
# TODO
# Implement turn off and on preview
# Implement camera light
# from pynput.keyboard import Key, Listener

import numpy as np
import picamera

from PIL import Image
from tflite_runtime.interpreter import Interpreter

# ================================ Detection Functions ================================
CAMERA_WIDTH = 300
CAMERA_HEIGHT = 300

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
    xmin = int(xmin * CAMERA_WIDTH)
    xmax = int(xmax * CAMERA_WIDTH)
    ymin = int(ymin * CAMERA_HEIGHT)
    ymax = int(ymax * CAMERA_HEIGHT)

    # Overlay the box, label, and score on the camera preview
    annotator.bounding_box([xmin, ymin, xmax, ymax])
    annotator.text([xmin, ymin],
                   '%s\n%.2f' % (labels[obj['class_id']], obj['score']))
    
  annotator.text([0, 460], f"Person count: {len(results)}")

# ================================ Data Handling Class ================================
# TODO Change to environment variable
SERVER_IP = "http://192.168.50.174:5000/"
ROUTE = f"{SERVER_IP}admin/pi" 

class Data(object):
  """Object to encapsulate data sending/preprocessing"""
  def __init__(self):
    self.data = dict()
    self.count = 0

  def process_result(self, results):
    """Processing routine called everytime image data comes in"""
    if self.count < 5:
      self.count += 1
      self.data[f'img{self.count}'] = len(results)
      print(self.data)
    else:
      self.count = 0
      self.data['average'] = sorted([value for value in self.data.values()])[2]
      self.data['timestamp'] = datetime.datetime.utcnow().isoformat(sep=' ', timespec='seconds')
      self.send_data(ROUTE)

  def send_data(self, endpoint):
    """Send data to the server"""
    try:
      r = requests.post(endpoint, json=self.data, timeout=0.5)
      r.raise_for_status()
    except:
      print("Could not send data")
    finally:
      self.data.clear()
      time.sleep(1)

def collect_data(switch, seconds):
  while True:
    try:
      time.sleep(seconds)
      switch.append(1)
    except KeyboardInterrupt:
      break

# ================================ Main Function ================================

def main():
  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
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
    default=0.4)
  parser.add_argument(
    '--watch', help='1 or 0',
    required=False,
    type=bool,
    default=0)
  args = parser.parse_args()

  labels = load_labels(args.labels)
  interpreter = Interpreter(args.model)
  interpreter.allocate_tensors()
  _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']

  # Init background thread. Switch is a list because python cannot pass by value
  switch = []
  t = threading.Thread(target=collect_data, args=[switch, 1])
  
  with picamera.PiCamera(
      resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30) as camera:
    camera.vflip = True
    camera.led = True
    on = args.watch
    D = Data()
    if on:
      camera.start_preview()
      time.sleep(2)
      t.start()
    while True:
      try:
        stream = io.BytesIO()
        annotator = Annotator(camera, "green")
        if on:
          for _ in camera.capture_continuous(stream, format='jpeg',
                                             resize=(input_width, input_height),
                                             use_video_port=True):
            stream.seek(0)
            image = Image.open(stream).convert('RGB')
            #.resize((input_width, input_height), Image.NEAREST)#Image.ANTIALIAS)
            
            start_time = time.monotonic()
            results = detect_objects(interpreter, image, args.threshold)
            elapsed_ms = (time.monotonic() - start_time) * 1000

            if len(switch):
              D.process_result(results)
              switch.clear()
            
            annotator.clear()
            annotate_objects(annotator, results, labels)
            annotator.text([5, 0], '%.1fms' % (elapsed_ms))
            annotator.update()
            stream.seek(0)
        else:
          camera.capture(stream, format='jpeg')
          stream.truncate()
          stream.seek(0)                
          image = Image.open(stream)
          results = detect_objects(interpreter, image, args.threshold)
          D.process_result(results)

      except KeyboardInterrupt:
        break


    print("Exitting")
    camera.stop_preview()
    t.join()

if __name__ == '__main__':
  main()
