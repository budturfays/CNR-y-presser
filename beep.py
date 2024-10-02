import os
import tempfile
import winsound
from tkinter import Toplevel, Label, Scale, Button, DoubleVar

def open_beep_window(root, textbox, update_status, reload_function, status, window, pick_method):
    beep_window = Toplevel(root)
    beep_window.title("Beeps")

    Label(beep_window, text="Frequency (Hz)").grid(row=0, column=0)
    Label(beep_window, text="Wave length (ms)").grid(row=1, column=0)
    Label(beep_window, text="Auto press cooldown (s)").grid(row=2, column=0)

    var1 = DoubleVar()
    var2 = DoubleVar()
    var3 = DoubleVar()

    scale1 = Scale(beep_window, variable=var1, from_=100, to=10000, orient='horizontal')
    scale1.grid(row=0, column=2)

    scale2 = Scale(beep_window, variable=var2, from_=100, to=3000, orient='horizontal')
    scale2.grid(row=1, column=2)

    scale3 = Scale(beep_window, variable=var3, from_=0, to=5, orient='horizontal')
    scale3.grid(row=2, column=2)

    # Default beep values
    var1.set(2000)
    var2.set(700)
    var3.set(3)

    def sample_beeps():
        winsound.Beep(int(var1.get()), int(var2.get()))

    def save_beeps():
        frequency = int(var1.get())
        wavelength = int(var2.get())
        cooldown = int(var3.get())
        update_status(textbox, f"Beep settings saved!")
        # Save the current beep settings to a file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "beep_settings.txt")
        with open(file_path, "w") as file:
            file.write(f"Frequency: {frequency} Hz\n")
            file.write(f"Wave length: {wavelength} ms\n")
            file.write(f"Cool down: {cooldown} s\n")
        update_status(textbox, f"Path: {file_path}")

    Button(beep_window, text="Load saved beep", command=lambda: load_beeps(textbox, var1, var2, var3, update_status)).grid(row=5, column=1)
    Button(beep_window, text="Play sample beep", command=sample_beeps).grid(row=3, column=1)
    Button(beep_window, text="Save", command=save_beeps).grid(row=4, column=1)
    
    reload_function(textbox, status, window, pick_method)
    beep_window.mainloop()

def load_beeps(textbox, var1, var2, var3, update_status):
    try:
        # Get the path to the Windows Temp folder
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "beep_settings.txt")
        # Read the file and insert its content
        with open(file_path, 'r') as f:
            lines = f.readlines()
            frequency = int(lines[0].split(": ")[1].strip().split(" ")[0])
            wavelength = int(lines[1].split(": ")[1].strip().split(" ")[0])
            cooldown = int(lines[2].split(": ")[1].strip().split(" ")[0])
        # Set the values in the GUI
        var1.set(frequency)
        var2.set(wavelength)
        var3.set(cooldown)
        update_status(textbox, f"Beeps loaded from: {file_path}")
    except Exception as e:
        update_status(textbox, f"Error loading beeps: {e}")
