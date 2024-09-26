import ctypes
from ctypes import wintypes
import tkinter as tk
from status_updater import *  # Assuming you have this function in a separate file

# Constants for GetDpiForMonitor
MDT_EFFECTIVE_DPI = 0

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

class MONITORINFOEX(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD),
        ("szDevice", wintypes.WCHAR * 32)
    ]

def get_display_scale(hmonitor):
    dpiX = wintypes.UINT()
    dpiY = wintypes.UINT()
    
    try:
        ctypes.windll.shcore.GetDpiForMonitor(
            hmonitor, MDT_EFFECTIVE_DPI, ctypes.byref(dpiX), ctypes.byref(dpiY)
        )
        return dpiX.value / 96.0  # 96 DPI is the default (100%) scale factor
    except Exception as e:
        print(f"Error getting DPI for monitor: {e}")
        return 1.0

def monitor_enum_proc(hmonitor, hdc, lprect, lparam):
    monitor_info = MONITORINFOEX()
    monitor_info.cbSize = ctypes.sizeof(MONITORINFOEX)

    if ctypes.windll.user32.GetMonitorInfoW(hmonitor, ctypes.byref(monitor_info)):
        scale = get_display_scale(hmonitor)
        is_primary = bool(monitor_info.dwFlags & 1)
        monitor_name = monitor_info.szDevice

        textbox, update_status_func = ctypes.cast(lparam, ctypes.POINTER(ctypes.py_object)).contents.value
        update_status_func(textbox, f"Monitor: {monitor_name}, Scale: {scale:.2f}, Primary: {is_primary}")
    
    return True

def set_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI awareness
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # System DPI awareness
        except Exception:
            pass

def show_disp_scale(textbox, update_status_func):
    set_dpi_awareness()

    # Pack textbox and update_status into a tuple and create a ctypes.py_object
    context = ctypes.py_object((textbox, update_status_func))

    # Define MonitorEnumProc
    MonitorEnumProc = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(RECT),
        wintypes.LPARAM
    )

    # Call EnumDisplayMonitors
    ctypes.windll.user32.EnumDisplayMonitors(
        None, 
        None, 
        MonitorEnumProc(monitor_enum_proc), 
        ctypes.cast(ctypes.pointer(context), ctypes.c_void_p)
    )
