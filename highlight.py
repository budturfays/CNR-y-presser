import threading
import win32gui
import tkinter as tk
from tkinter import TclError, messagebox

def get_relative_region(hwnd, relative_coords, window_resolution, manual_region=None):
    try:
        rect = win32gui.GetWindowRect(hwnd)
        win_left, win_top, win_right, win_bottom = rect
        win_width = win_right - win_left
        win_height = win_bottom - win_top
        
        if manual_region:
            # Manual region input is relative to the window
            left, top, right, bottom = manual_region

            # Convert relative manual region to absolute screen coordinates
            left = win_left + int(left)
            top = win_top + int(top)
            right = win_left + int(right)
            bottom = win_top + int(bottom)
        else:
            # Use default relative coordinates
            left, top, right, bottom = relative_coords

            scale_x = win_width / window_resolution[0]
            scale_y = win_height / window_resolution[1]

            left = int(win_left + left * scale_x)
            top = int(win_top + top * scale_y)
            right = int(win_left + right * scale_x)
            bottom = int(win_top + bottom * scale_y)

        width = right - left
        height = bottom - top

        return (left, top, width, height)
    except Exception as e:
        print(f"Error in get_relative_region: {e}")
        return None


def HighlightSection(Rect, Color='red', Duration=3):
    def create_highlight():
        left, top, width, height = Rect

        if width <= 0 or height <= 0:
            print(f"Invalid width or height: width={width}, height={height}")
            return

        win = tk.Tk()
        GeometryString = f"{width}x{height}+{left}+{top}"
        win.geometry(GeometryString)
        win.configure(background=Color)
        win.overrideredirect(1)
        win.attributes('-alpha', 0.3)
        win.wm_attributes('-topmost', 1)
        win.after(Duration * 1000, win.destroy)
        try:
            win.mainloop()
        except TclError:
            pass

    threading.Thread(target=create_highlight, daemon=True).start()


def open_manual_region_window(manual_region_var, hwnd):
    def on_submit():
        try:
            left = int(entry_left.get())
            top = int(entry_top.get())
            right = int(entry_right.get())
            bottom = int(entry_bottom.get())
            manual_region = (left, top, right, bottom)
            manual_region_var.set(str(manual_region))  # Store as a string
            manual_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integers for the region coordinates.")

    # Get the current window size for the PID
    try:
        rect = win32gui.GetWindowRect(hwnd)
        win_left, win_top, win_right, win_bottom = rect
        win_width = win_right - win_left
        win_height = win_bottom - win_top
    except Exception as e:
        print(f"Error getting window rect: {e}")
        win_left, win_top, win_right, win_bottom = 0, 0, 0, 0

    # Get the last input region if it exists
    last_region = manual_region_var.get()
    if last_region:
        last_left, last_top, last_right, last_bottom = eval(last_region)
    else:
        last_left, last_top, last_right, last_bottom = 0, 0, 0, 0

    manual_window = tk.Toplevel()
    manual_window.title("Manual Region Input")

    tk.Label(manual_window, text="Left:").grid(row=0, column=0)
    entry_left = tk.Entry(manual_window)
    entry_left.grid(row=0, column=1)
    entry_left.insert(0, str(last_left))  # Set last input value

    tk.Label(manual_window, text="Top:").grid(row=1, column=0)
    entry_top = tk.Entry(manual_window)
    entry_top.grid(row=1, column=1)
    entry_top.insert(0, str(last_top))  # Set last input value

    tk.Label(manual_window, text="Right:").grid(row=2, column=0)
    entry_right = tk.Entry(manual_window)
    entry_right.grid(row=2, column=1)
    entry_right.insert(0, str(last_right))  # Set last input value

    tk.Label(manual_window, text="Bottom:").grid(row=3, column=0)
    entry_bottom = tk.Entry(manual_window)
    entry_bottom.grid(row=3, column=1)
    entry_bottom.insert(0, str(last_bottom))  # Set last input value

    # Display the current PID window size
    tk.Label(manual_window, text=f"Current PID window size:\nLeft: {win_left}, Top: {win_top}, Width: {win_width}, Height: {win_height}").grid(row=4, column=0, columnspan=2)

    # Display the default relative coordinates
    tk.Label(manual_window, text=f"Default relative coordinates:\nLeft: 680, Top: 555, Right: 790, Bottom: 590").grid(row=5, column=0, columnspan=2)

    tk.Button(manual_window, text="Submit", command=on_submit).grid(row=6, column=0, columnspan=2)

    manual_window.mainloop()
