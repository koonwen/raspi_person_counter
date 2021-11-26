# Computer Vision
This repo contains the image detection code to be run on a Raspberry Pi. It also contains explanation of basic computer vision theory

# Motivation
With data privacy being a big concern and by striving to keep data transfer over the network low, it is a good idea to implement the image processing on the Pi itself which sends out only timestamps and integer values to our server. The current CV implementation uses the tensorflow-lite library and it's pre-packaged model for object detection. The OpenCV directory is a test bed for different CV frameworks. Future work may include training a custom model for the gym. Currently only detects people.

# Components
The main detection program that runs on the Raspberry Pi is found in `/tensor-flow/package`.

Within the directory, you will find the modules as follows:
- annotation.py: Class for drawing annotion boxes around detected objects (Used only for demo and development)
- camera.py: Camera class that provides interfaces to start detection in the background (during production) and watch background (testing purposes)
- coco_labels.txt: Labels that the model can detects
- data.py: Data class which encapsulates the logic and format of sending data to the cloud server
- detector.py: Detector class that makes use of tensorflow framework
- run.py: Program entry point defining flags for running program from the command line
- sig.py: Test bed for incorporating signalling I/O for our program (button to start and stop)
- test_cam.py: A small test program to check functionality of the picamera
- test_data.py: A small test program to check the functionality of sending data to the cloud server

# Refereneces
The code in this repo is adapted from https://github.com/tensorflow/examples/tree/master/lite/examples/image_classification/raspberry_pi. Credits to the authors of the TensorFlow-Lite Libraries and the Raspberry Pi tutorial!
