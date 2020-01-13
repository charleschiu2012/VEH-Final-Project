# # encoding: utf-8
import logging
import time

# Set logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M:%S')

#  PATH
SNAP_IMG_FOLDER = "./images"
SEGMENTATION_FOLDER = "./Results_segmentation"
RECOGNATION_FOLDER = "./Results_recognition"

# Socket
HOST = "127.0.0.1"
DRONE_PORT = 8889
YOLO_PORT = 8888
CM_PORT = 9999

# Basic stting
SNAP_IMAGE = "image.jpg"
DEFAULT_HEIGHT = 1.0
BASIC_ROTATE = 30
CLASS_INDEX = {"Charles": 0, "Alan": 1, "Peter": 2, "CM": 3}
CALLING_MACHINE_SIZE = [27.0, 13.0]
FRAME_SIZE = [960, 720]
CM_WIDTH_PIXEL = 220
CM_HEIGHT_PIXEL = 100
CM_DETECT_DISTANCE = 1.8
CUSTOMER_DETECT_DISTANCE = 3.0
QUALITY_THRESHOLD = 0.01
RANDOM_ROTATE = 2


def sleep(_time):
    time.sleep(_time)
