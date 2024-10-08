import psutil
import win32gui
import win32process
import tkinter as tk
from status_updater import update_status

def list_processes(textbox):
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            process_info = proc.info
            processes.append(process_info)
            update_status(textbox, f"PID: {process_info['pid']}, Name: {process_info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Skip processes that raise exceptions
    return processes

def find_default_pid(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            return proc.info['pid']
    return None

# Function to get the process window handle by PID
def get_process_handle_by_pid(pid):
    hwnds = []
    def callback(hwnd, hwnds):
        tid, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        if found_pid == pid:
            hwnds.append(hwnd)
    win32gui.EnumWindows(callback, hwnds)
    if hwnds:
        return hwnds[0]  # Return the first window handle associated with the PID
    else:
        return None
    
def auto_find_pid_on_startup(textbox, status, window):
    global pid, hwnd  # Declare as global to modify in this function
    
    # Attempt to automatically find a PID when the app starts
    process_name = "FiveM_b2545_GTAProcess.exe"
    selected_pid = find_default_pid(process_name)  # Function to find the default PID based on process name

    if selected_pid:
        update_status(textbox, f"Automatically selected PID {selected_pid}")
        status.set("Found the process automatically.")

        try:
            pid_name = get_process_name_from_pid(selected_pid)
            hwnd = get_process_handle_by_pid(selected_pid)

            if hwnd is not None:
                update_status(textbox, f"Window handle (HWND) found: {pid_name}")
            else:
                update_status(textbox, "Failed to find window handle.")

            # Set global variables
            pid = selected_pid
            hwnd = hwnd
            
            # Update status after a delay
            window.after(5000, lambda: status.set(f"Process: {pid_name} - HWND: {hwnd}"))

            return selected_pid, hwnd

        except Exception as e:
            update_status(textbox, f"Error while fetching process name: {e}")
            return None, None

    else:
        update_status(textbox, f"{process_name} not found. Retrying in 5 seconds.")
        status.set("Retrying...")
        # Retry after 5 seconds if the process is not found
        window.after(5000, lambda: auto_find_pid_on_startup(textbox, status, window))
        return None, None

def get_process_name_from_pid(pid):
    try:
        process = psutil.Process(pid)  # Create a process object
        return process.name()  # Return the process name
    except psutil.NoSuchProcess:
        return None  # If the process doesn't exist, return None
    except psutil.AccessDenied:
        return None  # If access is denied, return None
    except Exception as e:
        return None  # Return None in case of other exceptions
