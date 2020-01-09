# import argparse
import socket
import pickle
import segmentation
import recognition

# parser = argparse.ArgumentParser(description="arg parser")
# parser.add_argument("--filename", type=str, required=True, help="The filename of input image")
# args = parser.parse_args()

HOST = '127.0.0.1'  # 服务器的主机名或者 IP 地址
PORT = 9999  # 服务器使用的端口

if __name__ == "__main__":
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print("Here is 'Calling Machine'. Connected to server")

            # Notify server that here is "Calling Machine"
            s.sendall(b"Here is 'Calling Machine' !")

            # Receive frame from server
            # frame = s.recv(4096)
            # frame = pickle.loads(frame)
            # print('Received', frame)
            check = s.recv(4096)
            print("Received", check)
            if check == b"2":
                frame = "./images/img_crop.jpg"
                #----------------- Image segmentation -----------------#
                print("\n" + "="*30 + " Segmentation " + "="*30 + "\n")
                numbers = segmentation.main(frame)

                #------------------ Image recognition -----------------#
                print("="*30 + " Recognition " + "="*30 + "\n")
                pred_numbers = recognition.main(numbers)

                #------------- Show the prediction result -------------#
                print("\n" + "="*30 + " Prediction results " + "="*30)
                print("Prediction results:", pred_numbers)

                # Send prediction result back to server
                s.sendall(pickle.dumps(pred_numbers, protocol=2))
            else:
                # Send prediction result back to server
                s.sendall(b"Nothing")

            s.close()
    # frame = "F:/Tello_img/New folder/2020-01-08_16-23-53.jpg"
    # # ----------------- Image segmentation -----------------#
    # print("\n" + "=" * 30 + " Segmentation " + "=" * 30 + "\n")
    # numbers = segmentation.main(frame)
    #
    # # ------------------ Image recognition -----------------#
    # print("=" * 30 + " Recognition " + "=" * 30 + "\n")
    # pred_numbers = recognition.main(numbers)
    #
    # # ------------- Show the prediction result -------------#
    # print("\n" + "=" * 30 + " Prediction results " + "=" * 30)
    # print("Prediction results:", pred_numbers)
