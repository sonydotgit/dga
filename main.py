import tkinter as tk
from tkinter import ttk

import os
import sys
from multiprocessing import Process, Queue
from modules.get_training_data import get_data
from modules.train_model import train
from modules.capture_domain import capture


def create_bt(button_name):
    button = tk.Button(
            text=button_name,
            width=12,
            height=2,
            )
    return button

def hide_buttons():
    get_datasets_bt.destroy()
    train_model_bt.destroy()
    capture_domains_bt.destroy()
    exit_bt.destroy()

def display_buttons():
    global get_datasets_bt
    global train_model_bt
    global capture_domains_bt
    global provide_domain_bt
    global exit_bt

    exit_bt = create_bt("Exit")
    exit_bt.config(command=root.destroy)
    provide_domain_bt = create_bt("Provide Domain")
    provide_domain_bt.config(command=lambda: input_domain())
    get_datasets_bt = create_bt("Get Datasets")
    get_datasets_bt.config(command=lambda: view_progress("Getting Datasets", get_data))
    train_model_bt = create_bt("Train Model")
    train_model_bt.config(command=lambda: view_progress("Training Model", train))
    capture_domains_bt = create_bt("Capture Domains")
    capture_domains_bt.config(command=lambda: real_time())

def input_domain():
    pass

def real_time():
    pass

def view_progress(window_title, function_name):
    # create a new window
    progress_window = tk.Toplevel(root)
    progress_window.title(window_title)
    progress_window.geometry("500x200")

    # create progress bar and status label in new window
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
    progress_bar.pack(fill='both', padx=5, pady=5)

    status_label = tk.Label(progress_window, text="Initialising...")
    status_label.pack(padx=10, pady=10)

    # create a "Back" button to navigate back to main screen
    back_button = tk.Button(progress_window, text="Close", command=progress_window.destroy)
    back_button.pack(padx=10, pady=10)

    # Create a progress queue to communicate with the separate process
    progress_queue = Queue()

    # Create the separate process and pass the progress queue
    process = Process(target=function_name, args=(progress_queue,))
    process.start()
    while process.is_alive():
        if not progress_queue.empty():
            progress_int, progress_string = progress_queue.get()
            progress_var.set(progress_int)
            status_label.config(text=progress_string)
            progress_window.update_idletasks()

    status_label.config(text="Done")

def main():
    global root
    global status

    root = tk.Tk()
    root.geometry("520x260")
    root.title("DGA Detection")

    # Configure grid
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=4)
    root.columnconfigure(2, weight=1)

    # Create buttons for the
    # main screen
    display_buttons()

    # Position buttons
    get_datasets_bt.grid(row=0, column=1, pady=(10,10))
    train_model_bt.grid(row=1, column=1, pady=(10,10))
    capture_domains_bt.grid(row=2, column=0, pady=(10,10))
    provide_domain_bt.grid(row=2, column=2, pady=(10, 10))
    exit_bt.grid(row=2, column=1, pady=(10, 10))


    # add main label at bottom
    main_string = "Despite the awful look, it works."
    main_label = tk.Label(root, text=main_string, pady=20)
    main_label.grid(row=3, column=1)

    root.mainloop()

if __name__ == '__main__':
    main()
