import tkinter as tk
from tkinter import Text, Button, END
from PIL import Image, ImageTk
import win32gui
import cv2
import numpy as np
import time
import winsound
import threading
import tempfile
import ctypes
import mss
import mss.tools
#import pytesseract
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from paddleocr import PaddleOCR
#from paddleocr.tools.infer import predict_system
import logging
import paddle
import os
from dik import PressKey, ReleaseKey, DIK_Y
from status_updater import update_status
from process_handler import list_processes, auto_find_pid_on_startup
from highlight import get_relative_region, HighlightSection
from beep import load_beeps

# Initialize the stop event
stop_event = threading.Event()
ocr_thread = None
detection_thread = None

# Set logging level to WARNING or above
logging.getLogger("ppocr").setLevel(logging.ERROR)
paddle.disable_static()
SendInput = ctypes.windll.user32.SendInput

def open_proc_window(root):
    proc_window = tk.Toplevel(root)
    proc_window.title("Processes")
    txt_output = Text(proc_window, height=20, width=50)
    txt_output.pack(pady=5)
    processes = list_processes(txt_output)  # Assuming list_processes updates the textbox
    for process in processes:
        txt_output.insert(END, f"PID: {process['pid']}, Name: {process['name']}\n")
    exit_button = Button(proc_window, text="Exit", command=proc_window.destroy)
    exit_button.pack(pady=5)
  
def load_keywords(textbox):
    keywords = []
    try:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "keywords.txt")

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                keywords = [line.strip() for line in f.readlines() if line.strip()]
        else:
            update_status(textbox, "Keywords file not found.")
    except Exception as e:
        update_status(textbox, f"Error loading keywords: {e}")
    return keywords

import os
import tkinter as tk
from PIL import Image, ImageTk

def open_debugshot_window(screenshot_path, reference_image_path=None):
    parent = tk.Toplevel()
    parent.title("Screen Shot")

    try:
        # Load the screenshot
        print(f"Loading screenshot from: {screenshot_path}")
        screenshot_image = Image.open(screenshot_path)
        screenshot_photo = ImageTk.PhotoImage(screenshot_image)

        # Display the screenshot
        screenshot_label = tk.Label(parent, text="Screenshot")
        screenshot_label.pack()

        screenshot_display = tk.Label(parent, image=screenshot_photo)
        screenshot_display.image = screenshot_photo  # Keep reference to avoid garbage collection
        screenshot_display.pack()

        # If reference image exists, load and display it
        if reference_image_path and os.path.exists(reference_image_path):
            print(f"Loading reference image from: {reference_image_path}")
            reference_image = Image.open(reference_image_path)
            reference_photo = ImageTk.PhotoImage(reference_image)

            reference_label = tk.Label(parent, text="SS match reference Image")
            reference_label.pack()

            reference_display = tk.Label(parent, image=reference_photo)
            reference_display.image = reference_photo  # Keep reference to avoid garbage collection
            reference_display.pack()
        else:
            print("Reference image not provided or does not exist.")

        # Exit button to close the window
        exit_button = tk.Button(parent, text="Exit", command=parent.destroy)
        exit_button.pack(pady=5)

    except Exception as e:
        print(f"Error loading image: {e}")

    parent.mainloop()



def detect_and_press_y_OCR(hwnd, region, cooldown, frequency, wavelength, textbox, status, auto_shutdown, stop_event):
    last_y_time = time.time()
    shutdown_timeout = 5
    ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=True, det=False)
    count = 0
    last_press_time = 0
    keywords = load_keywords(textbox)
    update_status(textbox, f"Keywords loaded: {keywords}")

    def detect_offer_button():
        global screenshot_path    
        try:
            left, top, width, height = region
            if width <= 0 or height <= 0:
                return False

            with mss.mss() as sct:
                monitor = {"left": left, "top": top, "width": width, "height": height}
                screenshot = sct.grab(monitor)
                # Save the screenshot for debugging
                screenshot_path = "debug_region_ss.png"
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=screenshot_path)
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
                result = ocr.ocr(img, cls=True)
                if result and isinstance(result[0], list):
                    extracted_text = ' '.join([line[1][0] for line in result[0] if isinstance(line, list) and len(line) > 1 and isinstance(line[1], tuple)])
                    matched_keywords = [keyword for keyword in keywords if keyword.lower() in extracted_text.lower()]
                    update_status(textbox, f"{matched_keywords}")
                    return any(keyword.lower() in extracted_text.lower() for keyword in keywords)
                else:
                    return False
        except Exception as e:
            print(f"Error in detecting text: {e}")
            return False

    while not stop_event.is_set():
        if detect_offer_button():
            last_y_time = time.time()  # Reset the timer when "Y" is detected
            current_time = time.time()

            if current_time - last_press_time > cooldown:
                previous_hwnd = win32gui.GetForegroundWindow()
                force_foreground_window(hwnd)
                time.sleep(0.1)
                PressKey(DIK_Y)
                time.sleep(0.1)
                ReleaseKey(DIK_Y)
                winsound.Beep(frequency, wavelength)
                count += 1
                update_status(textbox, f"sold {count} times.")
                last_press_time = current_time
                force_foreground_window(previous_hwnd)
        else:
            current_time = time.time()
            if auto_shutdown.get() and current_time - last_y_time > shutdown_timeout:
                close_process(hwnd)
                shutdown_pc()
                break
            status.set(f"Detecting... {current_time - last_y_time:.0f}")

        time.sleep(2)  # Delay between checks
    print("OCR detection stopped.")




def reload(textbox, status, window, pick_method):
    global stop_event, ocr_thread

    # Signal the thread to stop
    stop_event.set()

    if ocr_thread is not None:
        ocr_thread.join()  # Wait for the OCR detection thread to finish
    
    # Reset the stop event for the next run
    stop_event.clear()
    
    # Clear the status and logs
    status.set("Reloading...")
    textbox.config(state=tk.NORMAL)
    textbox.delete("1.0", tk.END)  # Clear the textbox
    update_status(textbox, "Reloading process list...")

    # Refresh the process list
    list_processes(textbox)

    # Re-run the automatic PID finder
    pid, hwnd = auto_find_pid_on_startup(textbox, status, window)

    if pid is not None and hwnd is not None:
        update_status(textbox, f"Reloaded with PID {pid} and HWND {hwnd}")
        update_status(textbox, "Refreshing display scale... if freeze, re-open program")
        set_dpi_awareness()
        pick_method()
    else:
        update_status(textbox, "Reload failed to find a valid PID or HWND. Please check manually.")
        status.set("Manual input may be required.")

    
    textbox.config(state=tk.DISABLED)  # Optionally, disable the textbox after reloading


def force_foreground_window(hwnd):
    try:
        user32 = ctypes.windll.user32
        user32.AllowSetForegroundWindow(-1)  # ASFW_ANY
        user32.SetForegroundWindow(hwnd)
        print("Forced foreground window")
    except Exception as e:
        print(f"Failed to force foreground window: {e}")


def handle_window_interaction(hwnd, relative_coords, window_resolution, textbox, var1, var2, var3, status, auto_shutdown, manual_region, stop_event):
    if hwnd:
        force_foreground_window(hwnd)
        time.sleep(0.1)
       
        region = get_relative_region(hwnd, relative_coords, window_resolution, manual_region)
        if region:
            update_status(textbox, f"Region: {region}")
            HighlightSection(region)
            load_beeps(textbox, var1, var2, var3, update_status)
            update_status(textbox, f"Beeps loaded: {var1.get()}Hz {var2.get()}ms {var3.get()}s cooldown")
           
            detection_thread = threading.Thread(target=detect_and_press_y_OCR, args=(hwnd, region, var3.get(), var1.get(), var2.get(), textbox, status, auto_shutdown, stop_event))
            detection_thread.start()
           
            while detection_thread.is_alive():
                if stop_event.is_set():
                    detection_thread.join()
                    break
                time.sleep(1)
        else:
            print("Error in adjusting the region.")
    else:
        print("Window not found.")


def start_ocr_detection(pid, hwnd, textbox, var1, var2, var3, status, auto_shutdown, manual_region=None, stop_event=None):
    if pid and hwnd:
        relative_coords = (680, 555, 790, 590)
        window_resolution = (800, 600)
        
        if stop_event is None:
            stop_event = threading.Event()
        else:
            stop_event.clear()
        
        ocr_thread = threading.Thread(target=handle_window_interaction, args=(hwnd, relative_coords, window_resolution, textbox, var1, var2, var3, status, auto_shutdown, manual_region, stop_event))
        ocr_thread.start()
        
        update_status(textbox, "OCR detection started.")
        return ocr_thread
    else:
        update_status(textbox, "Failed to start OCR detection. PID or window handle not found.")
        return None
    

def close_process(hwnd):
    # Close the attached process
    print(f"Closing process with HWND: {hwnd}")
    ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
    time.sleep(100)

def shutdown_pc():
    # Shut down the PC
    os.system("shutdown /s /t 1")
    
PROCESS_SYSTEM_DPI_AWARE = 1
PROCESS_PER_MONITOR_DPI_AWARE = 2

def set_dpi_awareness():
    try:
        # This is available on Windows 8.1 and later
        ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
        print("DPI Awareness set to Per-Monitor DPI Aware")
    except Exception as e:
        try:
            # Fallback to older method available on Windows Vista and later
            ctypes.windll.user32.SetProcessDPIAware()
            print("DPI Awareness set to System DPI Aware")
        except Exception as e:
            print(f"Failed to set DPI Awareness: {e}")