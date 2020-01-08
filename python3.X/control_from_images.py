import tello
from tello_control_ui import TelloUI
import time
import something_to_detect_image as YOLO


def main():
    drone = tello.Tello('', 8889)
    vplayer = TelloUI(drone, "./img/")
    signal = YOLO(img_folder)
    time.sleep(10)
    drone.takeoff()
    time.sleep(10)
    drone.move_up(1)
    time.sleep(10)
    drone.land()
    time.sleep(10)
    vplayer.onClose()


if __name__ == "__main__":
    main()