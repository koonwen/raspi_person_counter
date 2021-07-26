from camera import start_background, watch_background
from detector import Detector
import argparse

if __name__ == "__main__":
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
    args = parser.parse_args()

    detector = Detector(args.model, args.labels, args.threshold)

    if args.watch:
        watch_background(detector)
    else:
        start_background(detector)
