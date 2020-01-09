# # encoding: utf-8
import tello
import socket
import threading
import pickle
import numpy as np
import time
import cv2
import os
from simple_pid import PID


def tune_with_pid(drone, frame, client_data, action, threshold=0.1):
    pid = PID(0.1, 0.1, 0.05, setpoint=1)
    speed = drone.get_speed()
    frame_h, frame_w, _ = frame.shape
    center_x, center_y = client_data[3], client_data[4]
    print "Translate drone frame shape: {} / {}".format(frame_h, frame_w)
    print "Translate drone center shape: {} / {}".format(center_x, center_y)
    if action == "control_height":
        height = drone.get_height()
        print(drone.get_speed())
        while height > threshold:
            direction = 'up'
            height = drone.get_height()
            distance = height - center_y
            control = pid(distance)
            drone.send_command('%s speed %s' % (direction, control))

    while distance > threshold:
        control = pid(distance)
        action(control)


def main():
    distance = 0.5
    degree = 30
    output_path = "./img/"
    drone = tello.Tello('', 8889)

    while True:
        control = raw_input("PLZ input: ")
        speed = raw_input("input speed: ")
        if control == "w":
            drone.send_command('%s speed %s' % ('up', speed))
            time.sleep(1)
            drone.set_speed(0)
        elif control == "s":
            drone.send_command('%s speed %s' % ('down', speed))
            time.sleep(1)
            drone.set_speed(0)
        elif control == "a":
            drone.send_command('cw %s' % degree)
        elif control == "d":
            drone.rotate_cw(degree)
        elif control == "i":
            drone.send_command('%s speed %s' % ('forward', speed))
            time.sleep(1)
            drone.set_speed(0)
        elif control == "k":
            drone.send_command('%s speed %s' % ('back', speed))
            time.sleep(1)
            drone.set_speed(0)
        elif control == "j":
            drone.send_command('%s speed %s' % ('left', speed))
            time.sleep(1)
            drone.set_speed(0)
        elif control == "l":
            drone.send_command('%s speed %s' % ('right', speed))
            time.sleep(1)
            drone.set_speed(0)

        if control == "t":
            drone.send_command('takeoff')
        if control == "g":
            drone.send_command('land')
            break
        if control == "/":
            snap_shoot(drone, output_path)

    print "Program end !!!"

