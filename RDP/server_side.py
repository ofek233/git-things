import socket
import pyautogui
import struct
from pynput.keyboard import Key
from PIL import Image
from io import BytesIO
import threading
import tkinter as tk
from PIL import Image, ImageTk
import time
import json


def send_packet(sock, payload_bytes):
    payload_bytes = payload_bytes if isinstance(payload_bytes, bytes) else payload_bytes.encode('utf-8')
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
    return payload

def on_press(key):
    try:
        return key.char
    except AttributeError:
        return key

# def on_release(key):
#     if key == keyboard.Key.esc:   # לעצור את זה
#         return False
#     return key

def keyboard(connection):
    print("Connected to client.")
    connection.send({"socket_type":"keyboard"})
    time.sleep(1)
    with keyboard.Listener(
        on_press=send_packet(connection, on_press)
        # on_release=on_release הסתבכתי קצת עם המימוש אז בנתיים פשוט אני מתעלם ממצב של החזקת מקשים
    ) as listener:
        listener.join()

def send_mouse(sock):
    x, y = pyautogui.position()
    button = 'none'
    if pyautogui.mouseDown(button='left'):
        button = 'left'
    elif pyautogui.mouseDown(button='right'):
        button = 'right'
    data = {'x': x, 'y': y, 'button': button}
    send_packet(sock, json.dumps(data).encode('utf-8'))
    time.sleep(0.01)

def tk_show_image(image):
    root = tk.Tk()
    tk_image = ImageTk.PhotoImage(image)
    label = tk.Label(root, image=tk_image)
    label.pack()
    root.mainloop()

def tk_show_images(queue): #ניסיון עם דרך אחרת
    root = tk.Tk()
    label = tk.Label(root)
    label.pack()

    def update():
        if not queue.empty():
            image = queue.get()
            tk_img = ImageTk.PhotoImage(image)
            label.config(image=tk_img)
            label.image = tk_img
        root.after(30, update)

    update()
    root.mainloop()

def handle_recived_screenShots(connection):
    while True:
        data = recv_packet(connection)
        image_from_data = Image.open(data)
        tk_show_image(image_from_data)


if __name__ == "__main__":

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = "127.0.0.1"
    udp_port = 8080
    tcp_port = 8081
    tcp_socket.bind(ip, tcp_port)
    tcp_socket.listen(2)
    print(f"Server listening on {ip}:{udp_port} (UDP) and on {ip}:{tcp_port} (TCP)")

    while True:
        udp_connection, udp_address = udp_socket.accept()
        if udp_connection:
            threading.Thread(target=handle_recived_screenShots, args=(udp_connection,)).start()
        connection, address = tcp_socket.accept()
        if connection:
            print(f"Connection established with {address}")
            socket_type = connection.recv().decode("utf-8")
            if socket_type == "keyboard":
                threading.Thread(target=keyboard, args=(connection,)).start()
            elif socket_type == "mouse":
                threading.Thread(target=send_mouse, args=(connection,)).start()
        if pyautogui.keyDown('esc'):
            print("Escape key pressed. Exiting.")
            break
    tcp_socket.close()
    udp_socket.close()
        