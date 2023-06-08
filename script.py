import pygetwindow as gw
import win32gui
import win32api
import win32con
import tkinter as tk
from tkinter import ttk
import threading

# Stocke les fenêtres actuellement transparentes
transparent_windows = []

# Obtient une liste de toutes les fenêtres ouvertes
def get_open_windows():
    windows = gw.getAllWindows()
    window_titles = [w.title for w in windows if w.visible and w.title != '' and w.title not in transparent_windows]
    return window_titles

# Rend une fenêtre transparente et la met en avant-plan
def set_transparent(window_title, listbox_active):
    hwnd = win32gui.FindWindow(None, window_title)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), 128, win32con.LWA_ALPHA)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
    transparent_windows.append(window_title)
    listbox_active.insert(tk.END, window_title)

# Rend une fenêtre opaque et la retire de l'avant-plan
def set_opaque(window_title, listbox_active):
    hwnd = win32gui.FindWindow(None, window_title)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & ~win32con.WS_EX_LAYERED)
    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
    transparent_windows.remove(window_title)
    listbox_active.delete(listbox_active.get(0, tk.END).index(window_title))

# Crée une interface utilisateur simple avec tkinter
def create_gui():
    window = tk.Tk()
    window.title("Windows Opacity Manager")
    window.geometry('500x400') 
    window.grid_columnconfigure(0, weight=1)
    window.grid_rowconfigure(0, weight=1)

    notebook = ttk.Notebook(window)
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    notebook.add(tab1, text='All Windows')
    notebook.add(tab2, text='Active Window')
    notebook.grid(row=0, column=0, sticky='nsew')

    listbox = tk.Listbox(tab1)
    listbox.pack(fill=tk.BOTH, expand=1)

    listbox_active = tk.Listbox(tab2)
    listbox_active.pack(fill=tk.BOTH, expand=1)

    transparent_button = tk.Button(window, text="Activer Transparence", command=lambda: set_transparent(listbox.get(tk.ANCHOR), listbox_active))
    transparent_button.grid(row=1, column=0, sticky='ew')

    opaque_button = tk.Button(window, text="Désactiver", command=lambda: set_opaque(listbox_active.get(tk.ANCHOR), listbox_active))
    opaque_button.grid(row=2, column=0, sticky='ew')

    #Slider pour la fenêtre du logiciel
    transparency_slider = tk.Scale(window, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, length=200,
                                  label="Set Application Window Opacity",
                                  command=lambda value: window.attributes('-alpha', float(value)))
    transparency_slider.set(1)  # Sets initial value to 1 (completely opaque)
    transparency_slider.grid(row=4, column=0, sticky='ew')

    #Slider pour la fenêtre choisie
    transparency_slider = tk.Scale(tab2, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, length=200,
                               label="Set Active Window Opacity")
    transparency_slider.set(0.5)  # Sets initial value to 1 (completely opaque)
    transparency_slider.pack()
    transparency_slider.bind("<B1-Motion>", lambda event: update_transparency(transparency_slider.get(), listbox_active))

    transparent_button = tk.Button(window, text="Make Transparent", command=lambda: set_transparent(listbox.get(tk.ANCHOR), listbox_active, transparency_slider.get()))
    opaque_button = tk.Button(window, text="Make Opaque", command=lambda: set_opaque(listbox_active.get(tk.ANCHOR), listbox_active, transparency_slider.get()))

    update_windows(listbox)
    
    window.mainloop()

# Enlève la fenêtre active de "All Windows" pour ne la laisser que dans fenêtre active
def update_windows(listbox):
    current_windows = get_open_windows()
    if sorted(listbox.get(0, tk.END)) != sorted(current_windows):
        selected = listbox.curselection()
        listbox.delete(0, tk.END)
        for window in current_windows:
            listbox.insert(tk.END, window)
        for i in selected:
            listbox.selection_set(i)
    listbox.after(1000, update_windows, listbox)

# Ajout d'un update à chaque fois qu'on touche au slider
def update_transparency(opacity, listbox_active):
    if listbox_active.get(tk.ANCHOR):
        window_title = listbox_active.get(tk.ANCHOR)
        hwnd = win32gui.FindWindow(None, window_title)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), int(float(opacity) * 255), win32con.LWA_ALPHA)

if __name__ == "__main__":
    create_gui()

