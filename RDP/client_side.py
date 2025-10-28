from io import BytesIO
import io
import socket
import keyboard
import pyautogui
import time
import struct
import pickle
from PIL import ImageGrab
import threading
import json


def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

# def send_data(conn, data):
#     serialized_data = pickle.dumps(data)
#     conn.sendall(struct.pack('>I', len(serialized_data)))
#     conn.sendall(serialized_data)

def send_tcp_packet(sock, payload_bytes):
    # payload_bytes is already bytes (e.g. encoded JSON or screenshot data)
    header = struct.pack('>I B', len(payload_bytes))
    sock.sendall(header + payload_bytes)

def send_udp_packet(sock, payload_bytes):
    # payload_bytes is already bytes (e.g. encoded JSON or screenshot data)
    header = struct.pack('>I B', len(payload_bytes))
    sock.sendall(header + payload_bytes)

# def receive_data(conn):
#     data_size = struct.unpack('>I', conn.recv(4))[0]
#     received_payload = b""
#     reamining_payload_size = data_size
#     while reamining_payload_size != 0:
#         received_payload += conn.recv(reamining_payload_size)
#         reamining_payload_size = data_size - len(received_payload)
#     data = pickle.loads(received_payload)
#     return data

def recv_packet(sock):
    # Read message length and type
    header = sock.recv(4)
    if not header:
        return None, None
    total_length = struct.unpack('>I B', header)

    # Read remaining payload
    payload = b''
    while len(payload) < total_length:
        chunk = sock.recv(min(4096, total_length - len(payload)))
        if not chunk:
            return None, None
        payload += chunk
    return payload


def handle_recived_keyboard():
    connection = connect_to_server(host, port)
    print("Connected to server. and waiting for keyboard data")
    socket.send({"socket_type":"keyboard"})
    while True: 
        #when reciving keyboard data from server
        key = recv_packet(connection).decode("utf-8")
        if key:
            pyautogui.press(key)


def handle_recived_mouse(connection):
    connect_to_server(host, port)
    print("Connected to server. and waiting for keyboard data")
    socket.send({"socket_type":"keyboard"})
    while True:
        #when reciving mouse data from server
        data = recv_packet(connection).decode("utf-8") #send to server
        if data:
            x, y, button = data.split(",")
            x, y = int(x), int(y)
            pyautogui.moveTo(x, y)
            if button == "left":
                pyautogui.click(button='left')
            elif button == "right":
                pyautogui.click(button='right')
        


# def screenshot():
#     connect_to_server(host, port)
#     print("Connected to server.")
#     socket.send({"socket_type":"screenshots"})
#     while True:
#         screenshot = ImageGrab.grab()
#         image_byte_array = BytesIO()
#         screenshot.save(image_byte_array, format='PNG')
#         image_byte_array.seek(0)
#         send_data(socket, image_byte_array)
#         time.sleep(0.1)

def send_screenshots():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((host, port))
    sock.send({"socket_type":"screenshots"})
    while True:
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        send_udp_packet(sock, buf.getvalue())
        time.sleep(0.05)


if __name__ == "__main__":
    host="127.0.0.1"
    port=8080


    threading.Thread(target=send_screenshots()).start()

    threading.Thread(target=handle_recived_keyboard()).start()

    threading.Thread(target=handle_recived_mouse()).start()

