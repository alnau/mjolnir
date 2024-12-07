import customtkinter as ctk
import time
import threading

from tkinter import *
from tkinter import ttk

class TopRow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master = parent,  height = 30, corner_radius=0)
        self.grid(row = 0, column = 0, columnspan = 5, rowspan = 1, pady = (2,2), padx = (2,2), sticky = "nwe")
        
        