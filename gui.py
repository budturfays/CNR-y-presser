import tkinter as tk
from tkinter import IntVar, Text, Radiobutton, Menu, StringVar
from misc import open_debugshot_window, open_proc_window, reload, start_ocr_detection, set_dpi_awareness
from process_handler import auto_find_pid_on_startup, list_processes, handle_enter
from status_updater import update_status
from keywords import open_keywords_window
from beep import open_beep_window
from disp import show_disp_scale
from sell import open_sell_window
from highlight import open_manual_region_window
from ssm import start_screenshot_comparison
import threading

detection_thread = None
ocr_thread = None
stop_event = threading.Event()

def start_gui():
    global pid, hwnd, auto_shutdown, manual_region_var  
    
    window = tk.Tk()
    window.title("1.3.4")

    window.geometry("330x205")
    set_dpi_awareness()
    auto_shutdown = tk.BooleanVar()
    manual_region_var = StringVar()  # Initialize manual_region_var as StringVar
    frame = tk.Frame(window)
    frame.pack()

    menubar = Menu(window)
    menu_guide = Menu(menubar, tearoff=0)
    menubar.add_cascade(menu=menu_guide, label='...')
    menu_guide.add_command(label="Selling places.", command=lambda: open_sell_window(window))
    menu_guide.add_command(label="Program guide.", command=lambda: update_status(textbox,"The program will find the window automatically, if not you have to enter by yourself \nPress reload every time the window changes places on any displays.\nLeave window open on any places the program will automatically force the window up.\nCheck the debug shot after reloading.\nPress reload the program will automatically adjust detection region based on your display scale. \nThe auto shutdown will exit the game and shutdown the PC after 300s from the last selling time.\nand the auto exit will quit the game after 300s from the last selling\nif you exit the game you have to restart the program again\nmanually input region need to be reloaded. if default region works don't put anything\nReset the program will reset the region."))
    menu_guide.add_command(label="Show all displays scale.", command=lambda: show_disp_scale(textbox, update_status))
    
    window.config(menu=menubar)

    # General settings section
    F1 = tk.LabelFrame(frame, text="General setting")
    F1.grid(row=0, column=0, pady=0, padx=5, sticky="news")

    # Method selection section
    F2 = tk.LabelFrame(frame, text="Methods")
    F2.grid(row=1, column=0, pady=0, padx=5, sticky="news")

    # Logs section
    F3 = tk.LabelFrame(frame, text="Logs")
    F3.grid(row=2, column=0, pady=0, padx=5, sticky="we")
    textbox = Text(F3, height=5, width=40, yscrollcommand=1)
    textbox.pack(fill=tk.BOTH, expand=True)

    status = tk.StringVar()
    status.set("Starting...")
    status_display = tk.Label(frame, textvariable=status)
    status_display.grid(row=3, column=0, sticky="ne")

    var1 = tk.IntVar()
    var2 = tk.IntVar()
    var3 = tk.IntVar()

    method = IntVar()
    method.set(1)  # Default selection for OCR method
    
    textbox.bind("<Return>", lambda event: handle_enter(event, textbox, status, pick_method))

    def pick_method():
        global detection_thread, ocr_thread, stop_event
        choice = method.get()
        # Extract manual_region from manual_region_var
        manual_region = eval(manual_region_var.get()) if manual_region_var.get() else None
        # Stop any ongoing detection (OCR or screenshot comparison)
        if stop_event:
            stop_event.set()  # Signal all threads to stop
            
        # Wait for threads to stop
        if ocr_thread and ocr_thread.is_alive():
            ocr_thread.join()
        if detection_thread and detection_thread.is_alive():
            detection_thread.join()
        # Create a new stop event
        stop_event = threading.Event()
        if choice == 1:  # OCR Method
            update_status(textbox, "OCR selected.")
            status.set("OCR set")
            # Start new OCR detection
            ocr_thread = threading.Thread(target=start_ocr_detection, args=(pid, hwnd, textbox, var1, var2, var3, status, auto_shutdown, manual_region, stop_event))
            ocr_thread.start()
        elif choice == 2:  # SS Comparing Method
            update_status(textbox, "SS matching selected.")
            status.set("SS matching...")
            # Start the screenshot comparison using the function in ssm.py
            detection_thread = start_screenshot_comparison(hwnd, textbox, update_status, var1, var2, var3, manual_region=manual_region, stop_event=stop_event, auto_shutdown=auto_shutdown)
        elif choice == 3:  # Both OCR and SS Comparing
            update_status(textbox, "OCR and SS matching selected.")
            status.set("OCR and SS matching set")
            ocr_thread = threading.Thread(target=start_ocr_detection, args=(pid, hwnd, textbox, var1, var2, var3, status, auto_shutdown, manual_region, stop_event))
            ocr_thread.start()
            detection_thread = start_screenshot_comparison(hwnd, textbox, update_status, var1, var2, var3, manual_region=manual_region, stop_event=stop_event, auto_shutdown=auto_shutdown)
        else:
            update_status(textbox, "Invalid method selected.")
            status.set("Invalid selection.")


    reference_image_path = "roi.png"
    screenshot_path = "debug_region_ss.png"
    
    # Button setup within General Settings (F1)
    reload_button = tk.Button(F1, text="Reload", command=lambda: reload(textbox, status, window, pick_method))
    reload_button.grid(row=0, column=0, padx=1)
    debug_button = tk.Button(F1, text="Debug shot", command=lambda: open_debugshot_window(screenshot_path, reference_image_path))
    debug_button.grid(row=0, column=1, padx=1)
    words_button = tk.Button(F1, text="Words", command=lambda: open_keywords_window(window, textbox, update_status, status, window, pick_method))
    words_button.grid(row=0, column=2, padx=1)
    beep_button = tk.Button(F1, text="Beeps", command=lambda: open_beep_window(window, textbox, update_status, reload, status, window, pick_method))
    beep_button.grid(row=0, column=3, padx=1)
    proc_button = tk.Button(F1, text="Procs.", command=lambda: open_proc_window(window))
    proc_button.grid(row=0, column=4, padx=1)
    manual_region_button = tk.Button(F1, text="Region", command=lambda: open_manual_region_window(manual_region_var, hwnd))
    manual_region_button.grid(row=0, column=5, padx=1)

    # Auto shutdown checkbutton
    c1 = tk.Checkbutton(frame, text='Auto shutdown', variable=auto_shutdown, onvalue=1, offvalue=0)
    c1.grid(row=3, column=0, sticky='nw')
    
    Radiobutton(F2, text="OCR", var=method, value=1, command=pick_method).grid(row=0, column=0, padx=10)
    Radiobutton(F2, text="SS match", var=method, value=2, command=pick_method).grid(row=0, column=1, padx=10)
    Radiobutton(F2, text="Both", var=method, value=3, command=pick_method).grid(row=0, column=2, padx=10)
    
    # Initialize PID and HWND
    pid, hwnd = auto_find_pid_on_startup(textbox, status, window)

    if pid is None or hwnd is None:
        update_status(textbox, "Failed to initialize PID or HWND.")
    else:
        # Proceed with method selection if PID and HWND are valid
        window.after(1000, lambda: pick_method())

    window.after(10, lambda: list_processes(textbox))
    window.mainloop()

if __name__ == "__main__":
    start_gui()
