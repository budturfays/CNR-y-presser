#status_updater
import tkinter as tk
from tkinter import font as tkfont

def update_status(textbox, message, font_size=7, font_family="Verdana"):
    try:
        # Set the font of the textbox
        custom_font = tkfont.Font(family=font_family, size=font_size)
        textbox.configure(font=custom_font)

        # Allow editing, insert message, and auto-scroll
        textbox.config(state=tk.NORMAL)
        textbox.insert("end", message + "\n")
        textbox.see("end")
    except Exception as e:
        # In case of error, print the exception to the console
        print(f"Error updating status: {e}")
    finally:
        # Ensure the textbox is always set to read-only state
        textbox.config(state=tk.DISABLED)

