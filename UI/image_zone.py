import customtkinter as ctk
import time
import threading

from tkinter import *
from tkinter import ttk
from PIL import Image as img
from PIL import ImageTk
import os



class ImageZone(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master = parent, corner_radius=2)
        self.grid(row = 1, column = 0, columnspan = 3, rowspan = 3, pady = (2,2), padx = (2,2), sticky = "nswe")
        
        path = "D:\Photonics\KGW МУР"
        name = "!18_d.tif"
        self.update()
        # size = (self.winfo_width(), self.winfo_height())
        size = (1280, 1024)
        self.image = ctk.CTkImage(img.open(os.path.join(path, name)), size = size)

        self.label = ctk.CTkLabel(parent, image= self.image, text = "")
        self.label.grid(row = 1, column = 0, columnspan = 3, rowspan = 3, sticky = "nswe", padx = (2,2), pady = (2,2))