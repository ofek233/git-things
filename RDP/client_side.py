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

def send_data(conn, data):
    serialized_data = pickle.dumps(data)
    conn.sendall(struct.pack('>I', len(serialized_data)))
    conn.sendall(serialized_data)

def receive_data(conn):
    data_size = struct.unpack('>I', conn.recv(4))[0]
    received_payload = b""
    reamining_payload_size = data_size
    while reamining_payload_size != 0:
        received_payload += conn.recv(reamining_payload_size)
        reamining_payload_size = data_size - len(received_payload)
    data = pickle.loads(received_payload)
    return data

def handle_recived_keyboard(connection):
    while True: 
        #when reciving keyboard data from server
        key = receive_data(connection) #send to server
        if not key:
            pass
        print(f"Received keyboard data: {key}")
        pyautogui.press(key)


def handle_recived_mouse(connection):
    while True:
        #when reciving mouse data from server
        data = receive_data(connection).decode("utf-8") #send to server
        if not data:
            pass
        x, y, button = data.split(",")
        x, y = int(x), int(y)
        pyautogui.moveTo(x, y)
        if button == "left":
            pyautogui.click(button='left')
        elif button == "right":
            pyautogui.click(button='right')

def screenshot():
    connect_to_server(host, port)
    print("Connected to server.")
    socket.send({"socket_type":"screenshots"})
    while True:
        screenshot = ImageGrab.grab()
        image_byte_array = BytesIO()
        screenshot.save(image_byte_array, format='PNG')
        image_byte_array.seek(0)
        send_data(socket, image_byte_array)
        time.sleep(0.1)

def send_screenshot(sock):
    img = ImageGrab.grab()
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=70)
    send_packet(sock, 3, buf.getvalue())

packet_type, payload = recv_packet(conn)
if packet_type == 1:
    mouse_data = json.loads(payload.decode())
elif packet_type == 2:
    key_data = json.loads(payload.decode())
elif packet_type == 3:
    with open('received.jpg', 'wb') as f:
        f.write(payload)


if __name__ == "__main__":
    host="127.0.0.1"
    port=8080
    threading.Thread(target=screenshot).start()
    threading.Thread(target=handle_recived_keyboard).start()
    threading.Thread(target=handle_recived_mouse).start()

