# # encoding: utf-8
import numpy as np
from config import *
import detect
import bridge


def pixel_to_meter(pixel):
    distance = pixel / 96 * 25.4 / 100

    return distance


def random_rotate(drone):
    magic = np.random.randint(2)
    if magic == 1:
        drone.rotate_cw(RANDOM_ROTATE)
    else:
        drone.rotate_ccw(RANDOM_ROTATE)


def rotate_drone(drone, client_data):
    """
    client_data: yolo_flag, class, confidence, center_x, center_y, width, height, left, top
    """
    frame_h, frame_w = FRAME_SIZE[0], FRAME_SIZE[1]
    center_x, center_y = client_data[3], client_data[4]
    bbox_w, bbox_h = client_data[5], client_data[6]
    print "Rotate drone bbox shape: {} / {}".format(bbox_w, bbox_h)
    print "Rotate drone frame shape: {} / {}".format(frame_w, frame_h)
    angle = 1 - (bbox_w / bbox_h) / (CALLING_MACHINE_SIZE[0] / CALLING_MACHINE_SIZE[1])

    if center_x > frame_w / 2:
        drone.rotate_cw(angle * BASIC_ROTATE)
    else:
        drone.rotate_ccw(angle * BASIC_ROTATE)
    sleep(1)


def translate_drone(drone, client_data):
    frame_h, frame_w = FRAME_SIZE[0], FRAME_SIZE[1]
    center_x, center_y = client_data[3], client_data[4]
    logging.info("Translate frame size: {} / {}".format(frame_h, frame_w))
    logging.info("Translate center: {} / {}".format(center_x, center_y))

    if center_x > frame_w / 2:
        distance = pixel_to_meter(center_x - (frame_w / 2))
        drone.move_right(distance)
    else:
        distance = pixel_to_meter((frame_w / 2) - center_x)
        drone.move_left(distance)

    if center_y < frame_h / 2:
        distance = pixel_to_meter((frame_h / 2) - center_y)
        drone.move_up(distance)
    else:
        distance = pixel_to_meter(center_y - (frame_h / 2))
        drone.move_down(distance)

    logging.info("Translate distance {}".format(distance))


def zoom_drone(drone, client_data):
    frame_h, frame_w = FRAME_SIZE[0], FRAME_SIZE[1]
    bbox_w, bbox_h = client_data[5], client_data[6]

    frame_area = frame_h * frame_w
    bbox_area = bbox_h * bbox_w
    logging.info("Frame Area {}, bbox Area {}".format(frame_area, bbox_area))
    logging.info("bbox_w / bbox_h {} / {}".format(bbox_w, bbox_h))

    if client_data[1] == CLASS_INDEX["CM"]:
        distance = (CM_DETECT_DISTANCE - (CM_DETECT_DISTANCE / CM_WIDTH_PIXEL) * bbox_w)
        logging.info("Distance from bbox center {}".format(distance))

        if distance > 0:
            drone.move_forward(distance)
            sleep(5)
    else:
        if abs(bbox_h - frame_h) > 100:
            distance = (CUSTOMER_DETECT_DISTANCE - (CUSTOMER_DETECT_DISTANCE/CM_WIDTH_PIXEL) * bbox_w)
            drone.move_forward(distance)
            drone.land()


def check_client_data(drone, server_yolo, name):
    _ = detect.get_frame(drone)
    client_data = bridge.get_client_data(server_yolo, True)
    if client_data.size == 0:
        return None
    idx = np.where(client_data[:, 1] == name)[0]
    if idx.size == 0:
        return None

    return client_data[idx][0]


def drone_move_type(drone, target_bbox, mode):
    print "Client_data {} {}".format(mode, target_bbox)

    if mode == "translate":
        translate_drone(drone, target_bbox)
    elif mode == "rotate":
        rotate_drone(drone, target_bbox)
    elif mode == "scale":
        zoom_drone(drone, target_bbox)


def check_cm_qaulity(drone, server_yolo):
    target_bbox = check_client_data(drone, server_yolo, CLASS_INDEX["CM"])
    if target_bbox is None:
        return False
    frame_h, frame_w = FRAME_SIZE[0], FRAME_SIZE[1]
    bbox_w, bbox_h = target_bbox[5], target_bbox[6]
    frame_area = frame_h * frame_w
    bbox_area = bbox_h * bbox_w
    print "(bbox_area / frame_area) = {} / {} = {}".format(bbox_area, frame_area, bbox_area / frame_area)
    return (bbox_area / frame_area) > QUALITY_THRESHOLD


def control_drone(drone, server_yolo, name):
    motion_list = ["translate", "rotate", "scale"]
    while not check_cm_qaulity(drone, server_yolo):
        for motion in motion_list:
            target_bbox = check_client_data(drone, server_yolo, name)
            if target_bbox is not None:
                drone_move_type(drone, target_bbox, motion)

    return True, True
