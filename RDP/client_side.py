from io import BytesIO
import io
import socket
import pyautogui
import time
import struct
from PIL import ImageGrab
import threading
from pynput.keyboard import Key, Controller
import json


def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket

def send_tcp_packet(sock, payload_bytes):
    header = struct.pack('>I', len(payload_bytes))
    sock.sendall(header + payload_bytes)

def send_udp_packet(sock, payload_bytes):
    header = struct.pack('>I', len(payload_bytes))
    sock.sendall(header + payload_bytes)

def recv_packet(sock):
    # Read message length
    header = sock.recv(4)
    if not header:
        return None, None
    total_length = struct.unpack('>I', header)
    # Read remaining payload
    payload = b''
    while len(payload) < total_length:
        chunk = sock.recv(min(4096, total_length - len(payload)))
        if not chunk:
            return None, None
        payload += chunk
    return payload.decode("utf-8")


def handle_recived_keyboard():
    keyboard = Controller()
    connection = connect_to_server(host, tcp_port)
    connection.sendall(json.dumps({"socket_type": "keyboard"}).encode())
    print("Connected to server. and waiting for keyboard data")
    time.sleep(1)
    while True: 
        #when reciving keyboard data from server
        key = recv_packet(connection)
        if key:
            keyboard.press(key)
            keyboard.release(key)

def handle_recived_mouse():
    conection = connect_to_server(host, tcp_port)
    conection.sendall(json.dumps({"socket_type": "keyboard"}).encode())
    print("Connected to server. and waiting for keyboard data")
    time.sleep(1)
    while True:
        #when reciving mouse data from server
        data = recv_packet(conection)
        if data:
            x, y, button = data.split(",")
            x, y = int(x), int(y)
            pyautogui.moveTo(x, y)
            if button == "left":
                pyautogui.click(button='left')
            elif button == "right":
                pyautogui.click(button='right')

def send_screenshots():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((host, udp_port))
    print("Connected to server. and starting to send screenshots")
    time.sleep(1)
    while True:
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        send_udp_packet(sock, buf.getvalue())
        time.sleep(0.05)


if __name__ == "__main__":
    host="127.0.0.1"
    udp_port=8080
    tcp_port=8081

    threading.Thread(target=send_screenshots).start()

    threading.Thread(target=handle_recived_keyboard).start()

    threading.Thread(target=handle_recived_mouse).start()

