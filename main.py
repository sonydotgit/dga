import tkinter as tk
from tkinter import ttk

import os
import sys
import time
from multiprocessing import Process, Queue
from modules.get_training_data import get_data
from modules.train_model import train
from modules.capture_domain import capture
from modules.predict import predict


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
    capture_domains_bt.config(command=lambda: view_progress("Capturing real time traffic", capture))

def onsubmit(stuff):
    progress_bar, progress_var, status_label = stuff

    domain_name = domain_entry.get()

    progress_queue = Queue()
    process = Process(target=predict,
                    args=(progress_queue, domain_name))

    process.start()
    while process.is_alive():
        if not progress_queue.empty():
            progress_int, progress_string = progress_queue.get()
            progress_var.set(progress_int)
            status_label.config(text=progress_string)
            get_domain_win.update_idletasks()

    time.sleep(4)
    get_domain_win.destroy()

def input_domain():
    global get_domain_win
    global domain_entry

    get_domain_win = tk.Toplevel(root)
    get_domain_win.geometry("340x250")
    get_domain_win.title("Input Domain")

    # configure the grid
    get_domain_win.columnconfigure(0, weight=1)
    get_domain_win.columnconfigure(1, weight=4)

    # add widgets
    domain_label = ttk.Label(get_domain_win, text="Entry Domain")
    domain_label.grid(column=0, row=0,
                        padx=5, pady=5,
                        sticky=tk.W)

    domain_entry = ttk.Entry(get_domain_win)
    domain_entry.grid(column=1, row=0,
                        padx=5, pady=5,
                        sticky=tk.W)


    # create a progress bar and a label
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(get_domain_win,
                                variable=progress_var,
                                maximum=100)
    progress_bar.grid(column=0, row=2, columnspan=2,
                    padx=5, pady=5)
    status_label = ttk.Label(get_domain_win,
                            text="Initialising...")
    status_label.grid(column=1, row=3,
                        padx=5, pady=5,
                        sticky=tk.W)

    submit_bt = ttk.Button(get_domain_win, text="Check",
            command=lambda: onsubmit((progress_bar,
                                    progress_var,
                                    status_label)))
    submit_bt.grid(column=1, row=1,
                    padx=5, pady=5,
                    sticky=tk.W)


def view_progress(window_title, function_name):
    # create a new window
    progress_window = tk.Toplevel(root)
    progress_window.title(window_title)
    progress_window.geometry("500x100")

    # create progress bar and status label in new window
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
    progress_bar.pack(fill='both', padx=5, pady=5)

    status_label = tk.Label(progress_window, text="Initialising...")
    status_label.pack(padx=10, pady=10)

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
    time.sleep(1)
    progress_window.destroy()

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


    root.mainloop()

if __name__ == '__main__':
    main()
