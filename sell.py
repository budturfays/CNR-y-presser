import tkinter as tk
from tkinter import font as tkfont, Toplevel

def open_sell_window(root):
    selling_window = Toplevel(root)
    selling_window.title("Selling place")
    selling_window.geometry("800x600")  # Set a size for the window as needed

    # Call create_table with the correct window (selling_window)
    create_table(selling_window)

def create_table(window):
    # Data for the table (based on your image)
    headers = ["Spot", "Coke", "Meth", "Heroin", "Acceptable Price", "ID", "Snitches"]
    spots = [
        ["Mission Row", "Low", "High", "Medium", "High", "14", "Medium"],
        ["Strawberry (Club)", "Low", "None", "Medium", "High", "3", "Low"],
        ["Vespucci Beach", "Medium", "Low", "Low", "High", "9", "Low"],
        ["Strawberry (Metro)", "None", "None", "Medium", "High", "4", "Low"],
        ["Rockford Hills", "High", "Low", "Low", "Medium", "13", "High"],
        ["West Vinewood", "High", "Low", "Medium", "Medium", "12", "Medium"],
        ["Burton", "Low", "High", "Medium", "Medium", "22", "Medium"],
        ["Davis (Ch. Hills)", "Low", "Medium", "None", "Medium", "7", "Medium"],
        ["East Vinewood", "Low", "High", "None", "Medium", "11", "Medium"],
        ["Little Seoul (Park)", "Low", "None", "Medium", "Medium", "8", "Medium"],
        ["Pacific Bluffs", "Low", "Low", "Medium", "Medium", "26", "Medium"],
        ["Paleto Bay", "Low", "Medium", "Low", "Medium", "17", "Medium"],
        ["Sandy Shores", "Low", "Medium", "Medium", "Medium", "16", "Medium"],
        ["Del Perro Beach", "Medium", "Low", "Medium", "Medium", "15", "Medium"],
        ["Del Perro Market", "Medium", "Low", "Medium", "Medium", "25", "High"],
        ["Downtown Vinewood", "Medium", "Low", "Low", "Medium", "20", "Medium"],
        ["Hawick", "Medium", "None", "Medium", "Medium", "28", "Low"],
        ["Mirror Park", "Medium", "Low", "Medium", "Medium", "10", "High"],
        ["Observatory", "Medium", "Low", "Medium", "Medium", "21", "Medium"],
        ["Vespucci Canals 1", "Medium", "Medium", "Low", "Medium", "18", "Low"],
        ["Rancho (Church)", "High", "Low", "Medium", "Low", "2", "Medium"],
        ["Davis (Grove St.)", "Low", "None", "Medium", "Low", "6", "Medium"],
        ["Rancho (Vagos)", "Low", "High", "Low", "Low", "1", "Medium"],
        ["Vespucci Canals 2", "Low", "Medium", "Low", "Medium", "19", "Low"],
        ["Davis (Metro)", "Medium", "None", "Medium", "Low", "5", "Medium"],
        ["LSIA", "Medium", "Low", "Medium", "Low", "27", "High"],
        ["Morningwood 1", "Medium", "Medium", "Medium", "Low", "23", "Low"],
        ["Morningwood 2", "Medium", "Medium", "None", "Low", "24", "High"],
    ]

    # Fonts
    header_font = tkfont.Font(family="Arial", size=10, weight="bold")
    cell_font = tkfont.Font(family="Arial", size=10)

    # Background colors based on the conditions
    def get_bg_color(text):
        if text == "High":
            return "#90EE90"  # Light Green
        elif text == "Medium":
            return "#F5F5A0"  # Light Yellow
        elif text == "Low":
            return "#FFC0CB"  # Light Pink
        else:
            return "white"

    # Create headers
    for i, header in enumerate(headers):
        tk.Label(window, text=header, font=header_font, borderwidth=1, relief="solid", padx=10, pady=5).grid(row=0, column=i, sticky="nsew")

    # Create data rows
    for i, row in enumerate(spots):
        for j, value in enumerate(row):
            bg_color = get_bg_color(value)
            tk.Label(window, text=value, font=cell_font, bg=bg_color, borderwidth=1, relief="solid", padx=10, pady=5).grid(row=i+1, column=j, sticky="nsew")

    # Configure grid weights to make the table expand proportionally
    for i in range(len(headers)):
        window.grid_columnconfigure(i, weight=1)
    for j in range(len(spots) + 1):
        window.grid_rowconfigure(j, weight=1)