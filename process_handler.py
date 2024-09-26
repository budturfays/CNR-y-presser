
#process_handler.py
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
    update_status(textbox, "Enter PID or press Enter to automatically select a PID")
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

            textbox.config(state=tk.DISABLED)  # Disable after auto-finding
            return selected_pid, hwnd

        except Exception as e:
            update_status(textbox, f"Error while fetching process name: {e}")
            return None, None

    else:
        update_status(textbox, "No suitable PID found automatically. Please manually enter a valid PID.")
        status.set("Manual input required.")
        textbox.config(state=tk.NORMAL)  # Enable textbox for manual input
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

def handle_enter(event, textbox, status, pick_method):
    global pid, hwnd

    # Enable the textbox for user input
    textbox.config(state=tk.NORMAL)

    # Get the user's input
    user_input = textbox.get("end-2c linestart", "end-1c").strip()

    if user_input:
        try:
            selected_pid = int(user_input)
            hwnd = get_process_handle_by_pid(selected_pid)

            if hwnd:
                pid = selected_pid
                process_name = get_process_name_from_pid(pid)
                status.set(f"Process: {process_name} - HWND: {hwnd}")

                # Debug print statements
                print(f"Successfully found HWND: {hwnd} for PID: {pid}")

                pick_method()  # Trigger the next step
                textbox.config(state=tk.DISABLED)
            else:
                update_status(textbox, f"No window handle found for PID {selected_pid}.")
                status.set("Failed to find window handle. Please try again.")
        except ValueError:
            update_status(textbox, "Invalid PID entered. Please enter a valid number.")
            status.set("Invalid input.")
        except Exception as e:
            update_status(textbox, f"An error occurred: {e}")
            status.set("Error processing input.")
    else:
        update_status(textbox, "No input provided. Please manually enter a valid PID.")
        status.set("No input provided.")

    textbox.delete("end-2c linestart", "end-1c")
    textbox.config(state=tk.NORMAL)