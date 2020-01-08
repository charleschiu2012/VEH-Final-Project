# # encoding: utf-8
import tello
import socket
import threading
import pickle
import numpy as np
import time
import cv2
import os
# from tello_control_ui import TelloUI

def get_socket_server(HOST, PORT):

    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print "[INFO] Listening on %s: %d" % (HOST, PORT)

    return server

def get_client_data(server_socket, frame, isYOLO):
    client_socket, address = server_socket.accept()
    print "[INFO] Acepted connection from: %s:%d" % (address[0],address[1])

    #---------- Receive the data from client ---------#
    client_data = client_socket.recv(1024)

    #------- Send the frame of drone to client -------#
    if isYOLO:
        client_socket.send(b"1")
    else:
        client_socket.send(b"2")
    
    client_data = client_socket.recv(4096)
    client_data = pickle.loads(client_data)
    print "Received data frome client: {}".format(client_data)

    #--------- Notify client that we get data --------#
    client_socket.send(b"Received")
    print "Notify client that we get data !!"

    return client_data

def get_frame(drone):
    frame = drone.read()

    if frame is None or frame.size == 0:
        return None
    else:
        cv2.imwrite("./images/image.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        return frame

def rotate_drone(drone, frame, client_data):
    frame_h, frame_w, _ = frame.shape
    center_x, center_y = client_data[3], client_data[4]
    bbox_w, bbox_h = client_data[5], client_data[6]
    print "Rotate drone bbox shape: {} / {}".format(bbox_w, bbox_h)
    print "Rotate drone frame shape: {} / {}".format(frame_w, frame_h)
    angle = 1 - (bbox_w / bbox_h) / (27.0 / 13.0)

    if center_x > frame_w / 2:
        drone.rotate_cw(angle * 30)
    else:
        drone.rotate_ccw(angle * 30)
    time.sleep(1)

def translate_drone(drone, frame, client_data):
    frame_h, frame_w, _ = frame.shape
    center_x, center_y = client_data[3], client_data[4]
    print "Translate drone frame shape: {} / {}".format(frame_h, frame_w)
    print "Translate drone center shape: {} / {}".format(center_x, center_y)

    if center_x > frame_w / 2:
        distance = (center_x - (frame_w / 2)) / 96 * 25.4 / 100
        drone.move_right(distance)
    else:
        distance = ((frame_w / 2) - center_x) / 96 * 25.4 / 100
        drone.move_left(distance)
    print "%f" %(distance)
    time.sleep(1)

    if center_y > frame_h / 2:
        distance = (center_y - (frame_h / 2)) / 96 * 25.4 / 100
        drone.move_up(distance)
    else:
        distance = ((frame_h / 2) - center_y) / 96 * 25.4 / 100
        drone.move_down(distance)
    print "%f" % (distance)
    time.sleep(1)

def forward_or_backward(drone, frame, client_data, isCM):
    frame_h, frame_w, _ = frame.shape
    bbox_w, bbox_h = client_data[5], client_data[6]

    frame_area = frame_h * frame_w
    bbox_area = bbox_h * bbox_w
    ratio = 0.03 if isCM else 0.3

    if bbox_area / frame_area < ratio:
        drone.move_forward(0.5)
        time.sleep(5)
        return "Not even closed"
    else:
        return "So closed"

def find_CM(drone, server_yolo):
    frame = get_frame(drone)
    client_data = get_client_data(server_yolo, frame, True)
    print "findCM: {}".format(client_data)

    if client_data.size == 0:
        drone.rotate_cw(30)
        return False

    if 3 in client_data[:, 1]:
        return True
    else:
        drone.rotate_cw(30)
        return False

def control_drone(drone, server_yolo):
    frame = get_frame(drone)
    client_data = get_client_data(server_yolo, frame, True)
    print "Client_data Rotate {}".format(client_data)
    if client_data.size == 0:
        return False, False
    rotate_drone(drone, frame, client_data[0])
    print "Rotate: {}".format(client_data)

    frame = get_frame(drone)
    client_data = get_client_data(server_yolo, frame, True)
    print "Client_data Translate {}".format(client_data)
    if client_data.size == 0:
        return False, False
    translate_drone(drone, frame, client_data[0])
    print "Translate: {}".format(client_data)

    frame = get_frame(drone)
    client_data = get_client_data(server_yolo, frame, True)
    print "Client_data Scale {}".format(client_data)
    if client_data.size == 0:
        return False, False
    isExtract = forward_or_backward(drone, frame, client_data[0], True)
    print "Scale: {}".format(client_data)

    return True, isExtract

def main(name, number):
    drone = tello.Tello('', 8889)  
    # vplayer = TelloUI(drone, "./img/")
    time.sleep(10)
    server_yolo = get_socket_server(HOST="127.0.0.1", PORT=8888)
    server_CM = get_socket_server(HOST="127.0.0.1", PORT=9999)

    isTakeOff = raw_input("Do you want to take off the drone? (yes / no)")
    if isTakeOff == "yes":
        drone.takeoff()
        time.sleep(10)
        drone.move_up(0.5)
        time.sleep(7)
        isFindCM = isExtract = False
        total_rotate = 0
        while True:
            if not isFindCM:
                isFindCM = find_CM(drone, server_yolo)
                total_rotate += 30
                if isFindCM:
                    print "\n\nEnd find CM\n\n"
                if total_rotate == 360:
                    total_rotate = 0
                    drone.move_up(0.3)
            else:
                total_rotate = 0
                isFindCM, isExtract = control_drone(drone, server_yolo)


            if isExtract == "So closed":
                print "\nisExtract!!!!!!!!!!!!!\n"
                frame = get_frame(drone)
                client_data = get_client_data(server_CM, frame, False)
                print "Input number: " + number
                print "Predicted number: {}".format(client_data)

                if len(client_data) != 3:
                    print "Invaild prediction result"
                elif number[0] == client_data[0] and number[1] == client_data[1] and number[2] == client_data[2]:
                    print "Good prediction!"

        while True:
            frame = get_frame(drone)
            client_data = get_client_data(server_yolo, frame, True)

            if name not in client_data[:, 1]:
                drone.rotate_cw(30)
                time.sleep(5)
            else:
                break

        while True:
            frame = get_frame(drone)
            client_data = get_client_data(server_yolo, frame, True)
            bbox_idx = np.where(client_data[:, 1] == name)[0][0]
            rotate_drone(drone, frame, client_data[bbox_idx])

            frame = get_frame(drone)
            client_data = get_client_data(server_yolo, frame, True)
            bbox_idx = np.where(client_data[:, 1] == name)[0][0]
            translate_drone(drone, frame, client_data[bbox_idx])
            
            frame = get_frame(drone)
            client_data = get_client_data(server_yolo, frame, True)
            bbox_idx = np.where(client_data[:, 1] == name)[0][0]
            isBack = forward_or_backward(drone, frame, cline_data[bbox_idx], False)

            if isBack == "So closed":
                drone.land()
                time.sleep(10)
                break

    print("Program end !!!")
    
	# # start the Tkinter mainloop
    # vplayer.root.mainloop() 

if __name__ == "__main__":
    # name = raw_input("PLZ input your name: ")
    # number = raw_input("PLZ input your waiting number: ")
    main(0, 420)
