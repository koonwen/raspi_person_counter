import os
import re
import numpy as np
from tflite_runtime.interpreter import Interpreter

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480


class Detector(object):
    """Detector class which acts as a wrapper for the tensor flow library API"""
    def __init__(self, model, path_to_label_file, threshold=0.4):
        self.interpreter = Interpreter(model)
        self.labels = self.load_labels(path_to_label_file)
        self.threshold = threshold
        _, self.input_height, self.input_width, _ = self.interpreter.get_input_details()[0]['shape']

    @staticmethod
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

    def set_input_tensor(self, image):
        """Sets the input tensor."""
        tensor_index = self.interpreter.get_input_details()[0]['index']
        input_tensor = self.interpreter.tensor(tensor_index)()[0]
        input_tensor[:, :] = image

    def get_output_tensor(self, index):
        """Returns the output tensor at the given index."""
        output_details = self.interpreter.get_output_details()[index]
        tensor = np.squeeze(self.interpreter.get_tensor(output_details['index']))
        return tensor

    def detect_objects(self, image):
        """Returns a list of detection results, each a dictionary of object info."""
        self.set_input_tensor(self.interpreter, image)
        self.interpreter.invoke()

        # Get all output details
        boxes = self.get_output_tensor(self.interpreter, 0)
        classes = self.get_output_tensor(self.interpreter, 1)
        scores = self.get_output_tensor(self.interpreter, 2)
        count = int(self.get_output_tensor(self.interpreter, 3))

        results = []
        for i in range(count):
            if scores[i] >= self.threshold and classes[i] == 0:
                result = {
                    'bounding_box': boxes[i],
                    'class_id': classes[i],
                    'score': scores[i]
                }
                results.append(result)
        return results

    @staticmethod
    def annotate_objects(self, annotator, results):
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
                           '%s\n%.2f' % (self.labels[obj['class_id']], obj['score']))