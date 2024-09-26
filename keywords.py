import os
import tempfile
from tkinter import Text, Button, END
import tkinter as tk
from misc import reload

def open_keywords_window(root, textbox, update_status, status, window, pick_method):

    keywords_window = tk.Toplevel(root)
    keywords_window.title("Keywords")

    label = tk.Label(keywords_window, text="Not case sensitive!")
    label.pack()

    # Create a text box for displaying keywords
    txt_output = Text(keywords_window, height=5, width=30)
    txt_output.pack(pady=5)

    keywords_list = ["Offer", "Y", "OfferY", "Offe"]
    # Insert keywords into the text box
    for item in keywords_list:
        txt_output.insert(END, item + "\n")

    # Function to automatically save keywords to the Windows Temp folder
    def save_keywords():
        # Get the path to the Windows Temp folder
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "keywords.txt")
        
        # Write the keywords to the file
        with open(file_path, 'w') as f:
            f.write(txt_output.get("1.0", END))
        
        update_status(textbox, f"Keywords automatically saved to {file_path}")
        reload(textbox, status, window, pick_method)

    def load_keywords():
        try:
            # Get the path to the Windows Temp folder
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, "keywords.txt")

            # Clear the Text widget before loading new content
            txt_output.delete("1.0", tk.END)

            # Read the file and insert its content into the Text widget
            with open(file_path, 'r') as f:
                keywords_list = f.readlines()
                for item in keywords_list:
                    txt_output.insert(tk.END, item)

            update_status(textbox, f"Keywords loaded from: {file_path}")
        except Exception as e:
            update_status(textbox, f"Error loading keywords: {e}")

    load_button = Button(keywords_window, text="Load saved list", command=load_keywords)
    load_button.pack(pady=1)
    
    # Create a save button to trigger saving
    save_button = Button(keywords_window, text="Save", command=save_keywords)
    save_button.pack(pady=1)
