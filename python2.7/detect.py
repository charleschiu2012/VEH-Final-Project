# # encoding: utf-8
import cv2
import bridge
from config import *


def get_frame(drone):
    frame = drone.read()
    if frame is None or frame.size == 0:
        return None
    else:
        cv2.imwrite(SNAP_IMG_FOLDER + "/" + SNAP_IMAGE, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        return frame


def find_calling_machine(drone, server_yolo, name):
    _ = get_frame(drone)
    client_data = bridge.get_client_data(server_yolo, True)
    print "find calling machine: {}".format(client_data)

    if client_data.size == 0:
        drone.rotate_cw(BASIC_ROTATE)
        return False

    if name in client_data[:, 1]:
        return True
    else:
        drone.rotate_cw(BASIC_ROTATE)
        return False
