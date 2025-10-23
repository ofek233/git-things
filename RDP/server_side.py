import socket
import pyautogui
import struct
import pickle
from PIL import Image
from io import BytesIO
import threading
import tkinter as tk
from PIL import Image, ImageTk
import time
import json


def tk_show_image(image):
    root = tk.Tk()
    tk_image = ImageTk.PhotoImage(image)
    label = tk.Label(root, image=tk_image)
    label.pack()
    root.mainloop()

def send_data(conn, data):
    serialized_data = pickle.dumps(data)
    conn.sendall(struct.pack('>I', len(serialized_data)))
    conn.sendall(serialized_data)

def send_packet(sock, packet_type, payload_bytes):
    # payload_bytes is already bytes (e.g. encoded JSON or screenshot data)
    header = struct.pack('>I B', len(payload_bytes) + 1, packet_type)
    sock.sendall(header + payload_bytes)

def receive_data(conn):
    data_size = struct.unpack('>I', conn.recv(4))[0]
    received_payload = b""
    reamining_payload_size = data_size
    while reamining_payload_size != 0:
        received_payload += conn.recv(reamining_payload_size)
        reamining_payload_size = data_size - len(received_payload)
    data = pickle.loads(received_payload)

    return data

def recv_packet(sock):
    # Read message length and type
    header = sock.recv(5)
    if not header:
        return None, None
    total_length, packet_type = struct.unpack('>I B', header)

    # Read remaining payload
    payload = b''
    while len(payload) < total_length - 1:
        chunk = sock.recv(min(4096, total_length - 1 - len(payload)))
        if not chunk:
            return None, None
        payload += chunk

    return packet_type, payload

def handle_recived_screenShots(connection):
    while True:
        data = receive_data(connection)
        image_from_data = Image.open(data)
        tk_show_image(image_from_data)

def keyboard(connection):
    #send data to connected client
    print("Connected to client.")
    connection.send({"socket_type":"keyboard"})
    while True:
        button = pyautogui.read_key()
        send_data(connection, button)
        time.sleep(0.1)



def mouse(connection):
    #send data to connected client
    print("Connected to client.")
    connection.send({"socket_type":"mouse"})
    while True:
        x, y = pyautogui.position()
        left_button = pyautogui.mouseDown()
        right_button = pyautogui.mouseDown(button='right')
        data = f"{x},{y},"
        if left_button:
            data += "left"
        elif right_button:
            data += "right"
        else:
            data += "none"
        # socket.send(data)
        send_data(connection, data)
        time.sleep(0.1)

def send_mouse(sock, x, y, button, state):
    data = {'x': x, 'y': y, 'button': button, 'state': state}
    send_packet(sock, 1, json.dumps(data).encode('utf-8'))

def send_key(sock, key, state):
    data = {'key': key, 'state': state}
    send_packet(sock, 2, json.dumps(data).encode('utf-8'))

packet_type, payload = recv_packet(conn)
if packet_type == 1:
    mouse_data = json.loads(payload.decode())
elif packet_type == 2:
    key_data = json.loads(payload.decode())
elif packet_type == 3:
    with open('received.jpg', 'wb') as f:
        f.write(payload)




socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = "127.0.0.1"
port = 8080
socket.bind((ip, port))
socket.listen(3)
print(f"Server listening on {ip}:{port}")

while True:
    print("Waiting for a connection...")
    connection, address = socket.accept()
    print(f"Connection established with {address}")
    socket_type = connection.recv().decode("utf-8")
    if socket_type == "keyboard":
        threading.Thread(target=keyboard(connection)).start()
    elif socket_type == "mouse":
        threading.Thread(target=mouse(connection)).start()
    elif socket_type == "screenshots":
        threading.Thread(target=handle_recived_screenShots(connection)).start()