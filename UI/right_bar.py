import customtkinter as ctk
import time
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tkinter import *
from tkinter import ttk

class RightBar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master = parent, corner_radius=2)
        self.grid(row = 1, column = 3, columnspan = 2, rowspan = 4, pady = (2,5), padx = (2,2), sticky = "ns")


        # Create a grid layout with 2 columns and 4 rows
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=2)
        self.grid_rowconfigure(3, weight =1)

        # Create a matplotlib figure and canvas
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [4, 5, 6])
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, columnspan=2, rowspan=1, padx = (2,2), pady = (2,2), sticky = "new")
        canvas.get_tk_widget().configure(width= 500)


        # Create a text field
        text_field = ctk.CTkEntry(self)
        text_field.grid(row=1, column=0, columnspan=2, rowspan=1, sticky="nsew", padx = (2,2), pady = (5,10))

        # self.line_style = ttk.Style()
        # self.line_style.configure("Line.TSeparator", background="#000000")
        # ttk.Separator(self,style="Line.TSeparator").grid(row = 2, column = 0, columnspan = 2, sticky = "ew", padx=10, pady=(10, 20))

        # Create two buttons in row 2
        button1 = ctk.CTkButton(self, text="Button 1")
        button1.grid(row=2, column=0, sticky="new", padx = (2,2), pady = (2,2))
        button2 = ctk.CTkButton(self, text="Button 2", )
        button2.grid(row=2, column=1, sticky="new", padx = (2,2), pady = (2,2))

        # Create two buttons in row 3
        button3 = ctk.CTkButton(self, text="Button 3", )
        button3.grid(row=3, column=0, sticky="new", padx = (2,2), pady = (2,2))
        button4 = ctk.CTkButton(self, text="Button 4", )
        button4.grid(row=3, column=1, sticky="new",padx = (2,2), pady = (2,2))
