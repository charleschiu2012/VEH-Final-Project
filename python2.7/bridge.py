# # encoding: utf-8
import pickle
import socket
from config import *


def get_socket_server(host, port):
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    logging.info("Listening on %s: %d" % (host, port))

    return server


def get_client_data(server_socket, yolo_flag):
    client_socket, address = server_socket.accept()
    # logging.info("Accepted connection from: %s:%d" % (address[0], address[1]))

    # ---------- Receive the data from client ---------#
    _ = client_socket.recv(1024)

    # ------- Send the frame of drone to client -------#
    if yolo_flag:
        client_socket.send(b"1")
    else:
        client_socket.send(b"2")

    client_data = client_socket.recv(4096)
    client_data = pickle.loads(client_data)
    logging.info("Received data from client: {}".format(client_data))

    # --------- Notify client that we get data --------#
    client_socket.send(b"Received")
    # logging.info("Notify client that we get data !!")

    return client_data
