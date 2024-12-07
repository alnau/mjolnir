import customtkinter as ctk
import time
import threading

from tkinter import *
from tkinter import ttk

class NavigationZone(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master = parent, height = 50, corner_radius=2)
        self.grid(row = 4, column = 0, columnspan = 3, rowspan = 1, pady = (2,5), padx = (2,2), sticky = "nswe")