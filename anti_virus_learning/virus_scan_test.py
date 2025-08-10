import os
import requests
import time
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# === VirusTotal API Key ===
API_KEY = '0b619e46ed0b55de12847453a1393f4c5e64a9adc3f2ecca913e94b1dfba6837'  # Replace with your actual key

# === Logger to the GUI ===
def log(message):
    try:
        output_box.insert(tk.END, str(message) + "\n")
        output_box.see(tk.END)
    except:
        output_box.insert(tk.END, "[Logging Error]\n")

# === VirusTotal Functions ===
def upload_file(file_path):
    url = 'https://www.virustotal.com/api/v3/files'
    headers = {'x-apikey': API_KEY}
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            log(f"Uploading file: {file_path}")
            response = requests.post(url, headers=headers, files=files)
        if response.status_code == 200:
            return response.json()['data']['id']
        else:
            log(f"Upload failed: {response.text}")
    except Exception as e:
        log(f"Error opening file: {e}")
    return None

def get_analysis(file_id):
    url = f'https://www.virustotal.com/api/v3/analyses/{file_id}'
    headers = {'x-apikey': API_KEY}
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            log(f"Error during analysis: {response.text}")
            return None
        data = response.json()
        status = data['data']['attributes']['status']
        if status == 'completed':
            return data['data']['attributes']['results']
        time.sleep(5)

def show_summary(results, file_path):
    log(f"\nScan results for: {file_path}")
    detected = False
    for engine, result in results.items():
        if result['category'] in ['malicious', 'suspicious']:
            detected = True
            log(f"[Detected] {engine}: {result.get('result', 'unknown')}")
    if not detected:
        log("No threats detected.")

def scan_file(file_path):
    try:
        if os.path.getsize(file_path) > 32 * 1024 * 1024:
            log(f"Skipping large file (>32MB): {file_path}")
            return
        file_id = upload_file(file_path)
        if file_id:
            results = get_analysis(file_id)
            if results:
                show_summary(results, file_path)
    except Exception as e:
        log(f"Scan error: {e}")

# === Full Folder Scan ===
def scan_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            scan_file(os.path.join(root, file))
            time.sleep(15)  # Prevent rate limit

# === Real-Time Monitoring ===
class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            log(f"New file detected: {event.src_path}")
            scan_file(event.src_path)

observer = None

def start_watching(folder_path):
    global observer
    log(f"Started real-time monitoring: {folder_path}")
    observer = Observer()
    observer.schedule(NewFileHandler(), folder_path, recursive=True)
    observer.start()

def stop_watching():
    global observer
    if observer:
        observer.stop()
        observer.join()
        observer = None
        log("Stopped real-time monitoring.")

# === GUI Logic ===
def choose_folder():
    folder = filedialog.askdirectory()
    folder_path_var.set(folder)

def start_scan_thread():
    folder = folder_path_var.get()
    if not os.path.isdir(folder):
        log("Please select a valid folder.")
        return
    log(f"\nStarting one-time scan for: {folder}\n")
    threading.Thread(target=lambda: scan_folder(folder), daemon=True).start()

def toggle_watch():
    folder = folder_path_var.get()
    if watch_var.get():
        if os.path.isdir(folder):
            threading.Thread(target=lambda: start_watching(folder), daemon=True).start()
        else:
            log("Please select a valid folder for monitoring.")
            watch_var.set(False)
    else:
        stop_watching()

# === GUI Setup ===
window = tk.Tk()
window.title("VirusTotal Folder Scanner")
window.geometry("780x600")
window.configure(bg='lightblue') # Set background color (for fun)

folder_path_var = tk.StringVar()
watch_var = tk.BooleanVar()

frame = tk.Frame(window)
frame.pack(pady=10)

tk.Label(frame, text="Folder to scan:").pack(side=tk.LEFT)
tk.Entry(frame, textvariable=folder_path_var, width=55).pack(side=tk.LEFT, padx=5)
tk.Button(frame, text="Browse", command=choose_folder).pack(side=tk.LEFT)

tk.Button(window, text="Start One-Time Scan", command=start_scan_thread).pack(pady=5)
tk.Checkbutton(window, text="Enable Real-Time Monitoring", variable=watch_var, command=toggle_watch).pack()

output_box = scrolledtext.ScrolledText(window, width=95, height=28, font=("Consolas", 10))
output_box.configure(bg='lightgrey', fg='black') # Set text box background and foreground color (for fun)
output_box.insert(tk.END, "Welcome to the VirusTotal Folder Scanner!\n")
output_box.insert(tk.END, "Select a folder and start scanning.\n")
output_box.pack(pady=10)

def on_closing():
    stop_watching()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
