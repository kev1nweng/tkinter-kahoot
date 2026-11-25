import tkinter as tk
from tkinter import ttk


class AppWindow(tk.Toplevel):
    def __init__(self, master, storage, title, size, minsize):
        super().__init__(master)
        self.storage = storage
        self.title(title)
        self.geometry(size)
        self.minsize(*minsize)
        self.body = ttk.Frame(self, padding=12)
        self.body.pack(fill="both", expand=True)

    def close(self):
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.destroy()
