from __future__ import absolute_import 
import threading
import time
import customtkinter as ctk
import CTkMessagebox as msg
from  tkinter import filedialog

from UI.top_row import TopRow
from UI.image_zone import ImageZone
from UI.right_bar import RightBar
from UI.navigation_zone import NavigationZone



ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):    
    def __init__(self):
        super().__init__()
        self.title("mjolnir")
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        height = int(0.8*screen_height)
        width = int(0.8*screen_width)
        self.geometry(f"{width}x{height}")

        
        self.setupGrid()

        self.topRow = TopRow(self)
        self.imageZone = ImageZone(self)
        self.rightBar = RightBar(self)
        self.navigation_zone = NavigationZone(self)



        
    def setupGrid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure((3,4), weight=0)

        self.grid_rowconfigure(0, weight= 0)
        self.grid_rowconfigure((1,2,3), weight=2)
        self.grid_rowconfigure(4, weight=0)


app = App()

app.update_idletasks()
app.mainloop()
# app.protocol("WM_DELETE_WINDOW", app.onClosing)
