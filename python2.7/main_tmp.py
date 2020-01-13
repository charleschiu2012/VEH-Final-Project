# # encoding: utf-8
import tello
import bridge
import detect
import movement
import os
from PIL import Image
import threading
from config import *


def get_number_from_string(_string):
    numbers = []
    for i in str(_string):
        numbers.append(int(i))

    return numbers


def check_flag(drone, server_yolo, name, total_rotate):
    find_flag = detect.find_calling_machine(drone, server_yolo, name)
    total_rotate += 30
    if total_rotate == 360:
        total_rotate = .0
        drone.move_up(0.3)

    return find_flag, total_rotate


def empty_folder(dir):
    files = os.listdir(dir)
    for file in files:
        os.remove(os.path.join(dir, file))


def videoLoop(drone):
    """
    The mainloop thread of Tkinter
    Raises:
        RuntimeError: To get around a RunTime error that Tkinter throws due to threading.
    """
    try:
        # start the thread that get GUI image and drwa skeleton
        time.sleep(0.5)
        while True:

            # read the frame for GUI show
            frame = drone.read()
            if frame is None or frame.size == 0:
                continue

                # transfer the format from frame to image
            image = Image.fromarray(frame)



def main(name, number):
    drone = tello.Tello('', DRONE_PORT)
    sleep(10)
    server_yolo = bridge.get_socket_server(HOST, YOLO_PORT)
    server_cm = bridge.get_socket_server(HOST, CM_PORT)

    takeoff_flag = raw_input("Do you want to take off the drone? (y / n)")
    if takeoff_flag == "y":
        drone.takeoff()
        sleep(5)
        drone.move_up(DEFAULT_HEIGHT)
        find_cm_flag = False
        extract_flag = False
        total_rotate = .0
        while True:
            if not find_cm_flag:
                find_cm_flag, total_rotate = check_flag(drone, server_yolo, CLASS_INDEX["CM"], total_rotate)
            else:
                total_rotate = 0
                find_cm_flag, extract_flag = movement.control_drone(drone, server_yolo, CLASS_INDEX["CM"])

            if extract_flag:
                logging.info("Image been extracted!")
                break

        while True:
            _ = detect.get_frame(drone)
            _ = bridge.get_client_data(server_yolo, False)
            client_data = bridge.get_client_data(server_cm, False)
            logging.info("Input number: {}".format(number))
            logging.info("Predicted number: {}".format(client_data))
            numbers = get_number_from_string(number)

            if len(client_data) != 3:
                logging.info("Prediction failed")
                movement.random_rotate(drone)
            elif numbers[0] == client_data[0] and numbers[1] == client_data[1] and numbers[2] == client_data[2]:
                logging.info("\n\nPrediction succeeded!\n\n")
                break
            else:
                logging.info("\n\nWhat are you doing now???????\n\n")
            drone.rotate_cw(RANDOM_ROTATE)
            drone.rotate_ccw(RANDOM_ROTATE)

            empty_folder(SEGMENTATION_FOLDER)

        find_customer_flag = False
        zone_flag = False
        total_rotate = 0
        while True:
            if not find_customer_flag:
                find_customer_flag, total_rotate = check_flag(drone, server_yolo, name, total_rotate)
            else:
                total_rotate = 0
                find_customer_flag, zone_flag = movement.control_drone(drone, server_yolo, name)

            if zone_flag == "So closed":
                logging.info("\n\n\nFind Costumer!\n\n\n")
                drone.land()
                break

        # while True:
        #     _ = get_frame(drone)
        #     client_data = get_client_data(server_yolo, True)
        #
        #     if name not in client_data[:, 1]:
        #         drone.rotate_cw(30)
        #         time.sleep(5)
        #     else:
        #         break
        #
        # while True:
        #     frame = get_frame(drone)
        #     client_data = get_client_data(server_yolo, True)
        #     bbox_idx = np.where(client_data[:, 1] == name)[0][0]
        #     # rotate_drone(drone, frame, client_data[bbox_idx])
        #
        #     frame = get_frame(drone)
        #     client_data = get_client_data(server_yolo, True)
        #     bbox_idx = np.where(client_data[:, 1] == name)[0][0]
        #     translate_drone(drone, frame, client_data[bbox_idx])
        #
        #     frame = get_frame(drone)
        #     client_data = get_client_data(server_yolo, True)
        #     bbox_idx = np.where(client_data[:, 1] == name)[0][0]
        #     isBack = forward_or_backward(drone, frame, cline_data[bbox_idx], False)
        #
        #     if isBack == "So closed":
        #         drone.land()
        #         time.sleep(10)
        #         break

    logging.info("Program end !!!")


if __name__ == "__main__":
    # name = raw_input("PLZ input your name: ")
    # number = raw_input("PLZ input your waiting number: ")
    main(2, 420)


