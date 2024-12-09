import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import numpy as np
from PIL import ImageDraw

import camera_feed as camera
from camera_feed import cameraFeed

import constants as const

import threading
import time
from datetime import datetime

import tkinter as tk
from  tkinter import filedialog

from CTkMenuBar import *

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class NavigationFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # self.right_frame_handle = right_frame_handle

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", pady=10, padx = 2, side = 'top')
        self.button_frame.grid_columnconfigure(0, weight=3)
        self.button_frame.grid_columnconfigure(1, weight=3)
        
        self.prev_button = ctk.CTkButton(self.button_frame, text="<", command = lambda: print('click'))
        self.prev_button.grid(row = 0, column = 0, sticky = 'e', padx = 10, pady = 5)
        # self.button1.pack(side="left", padx=10, pady=5)

        self.next_button = ctk.CTkButton(self.button_frame, text=">")
        self.next_button.grid(row = 0, column = 1, sticky = 'w', padx = 10, pady = 5)
        # self.button2.pack(side="right", padx=10, pady=5)

class LeftFrame(ctk.CTkFrame):
    def __init__(self, master, right_frame_handle, image_path, **kwargs):
        super().__init__(master, **kwargs)

        # shared_image = {}

        # # Start the camera feed thread
        # camera_thread = threading.Thread(target=cam.cameraFeed, args=(shared_image,))
        # camera_thread.daemon = True  # Daemonize the thread to stop it when the main program exits
        # camera_thread.start()

        # # Start the periodic update of the canvas
        # self.update_canvas(shared_image)

        self.right_frame_handle = right_frame_handle

        self.start_coords = (0,0)
        self.tmp_coords = (0,0)
        self.end_coords = (0,0)


        self.image_path = image_path
        self.image_canvas = tk.Canvas(self)
        self.image_canvas.pack(fill="both", padx = (5,0), pady = 5, expand=True)
        self.image = Image.open(self.image_path)

        # Bind the <Configure> event to resize the image
        
        self.bind("<Configure>", self.resize_image)
        self.image_canvas.bind("<ButtonPress-1>", self.drawLines )
        self.image_canvas.bind("<B1-Motion>", self.drawLines )
        self.image_canvas.bind("<ButtonRelease-1>", self.drawLines )
        self.image_canvas.bind("<ButtonRelease-1>", self.drawLines )


        # Load and display the initial image
        self.resize_image(None)

    def drawLines(self, event):
        if (self.master.right_frame.photo_is_captured or self.master.right_frame.tabview.get() == 'Обработка'):
            if (event.type == '4'):
                self.master.right_frame.tabview.check_var.set('on')
                self.tmp_coords = (0,0)
                self.start_coords = (event.x, event.y)
            elif (event.type == '5'):
                self.end_coords = (event.x, event.y)
                self.tmp_coords = self.end_coords
                p0_real_coords = (self.start_coords[0]*self.image.width/self.image_resized.width, self.start_coords[1]*self.image.height/self.image_resized.height)
                p1_real_coords = (self.end_coords[0]*self.image.width/self.image_resized.width, self.end_coords[1]*self.image.height/self.image_resized.height)
                self.right_frame_handle.updatePlot(p0_real_coords, p1_real_coords)
            elif (event.type == '6'):
                # if (self.start_coords == (0,0)):
                #     self.start_coords = (event.x, event.y)
                # else:
                self.tmp_coords = (event.x, event.y)
            if (self.tmp_coords != (0,0)):
                updated_image = self.updateLineOnPhoto()

            photo = ImageTk.PhotoImage(updated_image)

            # Update the label with the resized image
            self.image_canvas.config(width=updated_image.width, height=updated_image.height)
            self.image_canvas.image = photo
            self.image_canvas.create_image(0,0,image=photo,anchor = 'nw')
        else:
            self.master.right_frame.logStatus("Необходимо сначала захватить изображение")

    def update_canvas(self, shared_image):
        if 'image' in shared_image:
            img = shared_image['image']
            resized_img = img.resize((self.winfo_width(), self.winfo_height()), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(resized_img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo  # Keep a reference to avoid garbage collection
        self.canvas.after(100, self.update_canvas, shared_image)  # 10 Hz refresh rate


        

    def getCircleBound(self, point, r):
        return (point[0]-r,point[1]-r, point[0]+r, point[1]+r)
        

    def updateLineOnPhoto(self):
        tmp_image = self.image_resized.copy()

        width, height = tmp_image.size


        draw = ImageDraw.Draw(tmp_image)


        line_color = (255,255,255)  
        line_width = 2  # Width of the line
        circle_radius = 2
        draw.ellipse(self.getCircleBound(self.start_coords, circle_radius), fill = line_color, width = line_width)
        draw.ellipse(self.getCircleBound(self.tmp_coords, circle_radius), fill = line_color, width = line_width)
        draw.line([self.start_coords, self.tmp_coords], fill = line_color, width = line_width)
        return tmp_image
    
    def clearPhoto(self):
        tmp_image = self.image_resized.copy()

        photo = ImageTk.PhotoImage(tmp_image)

        # Update the label with the resized image
        self.image_canvas.config(width=tmp_image.width, height=tmp_image.height)
        self.image_canvas.image = photo
        self.image_canvas.create_image(0,0,image=photo,anchor = 'nw')


    
    def resize_image(self, event):
        # Get the current size of the frame
        # image = Image.open(self.image_path)
        width = self.winfo_width()
        height = self.winfo_height()

        # Load and resize the image to fit the frame
        image = self.image
        self.image_resized = image.resize((width, height))
        self.photo = ImageTk.PhotoImage(self.image_resized)

        # Update the label with the resized image
        self.image_canvas.config(width=self.image_resized.width, height=self.image_resized.height)
        self.image_canvas.image = self.photo
        self.image_canvas.create_image(0,0,image=self.photo,anchor = 'nw')

class RightFrame(ctk.CTkFrame):
    def __init__(self, master, camera_handle, **kwargs):
        super().__init__(master, **kwargs)

        self.photo_is_captured = False
        # Create a matplotlib figure with a 2:1 aspect ratio
        self.fig, self.ax = plt.subplots(figsize=(5, 3))  # 4:2 aspect ratio
        self.ax.plot([1, 2, 3], [4, 5, 6])
        self.ax.set_aspect('auto', adjustable='box')

        # Create a canvas to embed the plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="x", padx = 5, pady = (5,0), side = "top")

        # Add an entry field just under the plot
        self.entry_frame = ctk.CTkFrame(self, )
        self.entry_frame.pack(fill="x", pady=(10, 5), side = 'top')
        
        self.entry = ctk.CTkEntry(self.entry_frame)
        self.entry.pack(fill="x", side = 'left', padx=2, pady=2, expand = True)
        
        self.capture_button = ctk.CTkButton(self.entry_frame, text = 'Захватить', command= self.captureImage)
        self.capture_button.pack(side = 'left', pady = 2, padx = (2,2))
    


        # Add a thin frame just under the entry field
        self.thin_frame = ctk.CTkFrame(self, height=2, bg_color="gray")
        self.thin_frame.pack(fill="x", padx =10, pady=5,)

        # self.empty_frame = ctk.CTkFrame(self, fg_color='transparent')
        # self.empty_frame.pack(fill="x", expand = True)

        self.tabview = Tab(master = self, main=master)
        self.tabview.pack(side = 'top', fill = 'both', expand = True) 
        
        self.continue_button = ctk.CTkButton(master = self, command = self.nextImage, text = 'Продолжить', state = 'disabled')
        self.continue_button.pack(side = 'top', fill = 'x')

        self.status_frame = ctk.CTkFrame(self, )
        self.status_frame.pack(fill="x", pady=10, padx = 2,  side = 'top')

        self.status = ctk.CTkLabel(self.status_frame, text = '', height = master.navigation_frame.button_frame.winfo_height() + 25 )   
        self.status.pack( fill = 'x', pady = 5, side = 'top')

    def logStatus(self, text_to_log):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        # new_text = "\n" + current_time + ": " + text_to_log 
        # self.status.insert('end', new_text)
        t_col = self.status.cget('text_color')
        new_text = current_time + ": " + text_to_log
        self.status.configure(text = text_to_log, text_color = 'red')
        threading.Thread(target=self.fadeInColor, args=(), daemon=True).start()

    def fadeInColor(self):
        for i in range(11):
            r = 255
            g = 25*i
            b = 25*i
            color = f'#{r:02x}{g:02x}{b:02x}'  # Convert to hex color
            self.status.configure( text_color=color)  # Update label color
            time.sleep(0.05)  # Sleep for 50ms (0.5 seconds total) 


    def captureImage(self):
        # захват текущего изображения
        
        if (self.photo_is_captured):
            # возможно, происходит очистка собранных данных
            # переход к живой камере
            self.capture_button.configure(text = 'Захватить')
            self.photo_is_captured = False
            self.master.left_frame.clearPhoto()
            self.continue_button.configure(state = 'disabled')

        else:
            # Показать картинку, сохранить в буффер
            self.capture_button.configure(text = 'Отмена')
            self.photo_is_captured = True
            self.continue_button.configure(state = 'enabled')
        

    def nextImage(self):
        # TODO сохранение данных
        self.master.left_frame.clearPhoto()
        self.tabview.check_var.set('off' )
        self.logStatus('Данные записаны')

    def updatePlot(self, p0, p1): 
        self.ax.clear()
        # TODO здесь должна быть функция, возвращающая точки распределения из ImageData
        # self.tabview.slider.configure(button_color = const.FG_COLOR )
        # self.capture_button.configure(state = 'normal', fg_color = const.FG_COLOR)
        # if (max(brightness) = 255):
        #   self.capture_button.configure(state = 'disabled', fg_color = 'red')
        #   self.tabview.slider.configure(button_color = 'red' )
        self.ax.plot([p0[0], p1[0]], [p0[1], p1[1]])
        self.canvas.draw()


class Tab(ctk.CTkTabview):
    def __init__(self, master, main, **kwargs):
        super().__init__(master, **kwargs)

        self.main = main

        self.configure(command = self.lockNavigation)

        self.pack(fill="x", expand = True)

        self.capture_tab = self.add("Захват")  
        self.analyse_tab = self.add("Обработка")  
        
        
        self.slider_frame = ctk.CTkFrame(self.capture_tab, fg_color='transparent')
        self.slider_frame.pack(fill = 'x', side = 'top')

        self.slider_label = ctk.CTkLabel(self.slider_frame, text='Экспозиция    ')
        self.slider_label.pack(side = 'left')
        self.slider = ctk.CTkSlider(self.slider_frame, from_ = 0,to = const.MAX_EXPOSURE_MS, command = self.sliderEvent)
        self.slider.pack(fill = 'x', side = 'left', expand = True)
        # print(self.slider.cget('progress_color'), self.slider.cget('button_color')) 

        self.option_frame = ctk.CTkFrame(self.capture_tab, fg_color='transparent')
        self.option_frame.pack(side = 'top', fill = 'x', pady = (10,0))
        
    
        self.check_var = ctk.StringVar(value="off")
        self.select_optimisation_button = ctk.CTkCheckBox(self.option_frame, onvalue= 'on', offvalue = 'off', variable= self.check_var, text = 'Использовать пользовательскую линию для анализа')
        self.select_optimisation_button.grid(sticky = 'nw')

        self.lockNavigation()

    def sliderEvent(self, val):
        camera.setExposure(camera=self.main.cam, exposure_time_ms = val)

    def lockNavigation(self):
        if (self.get() == 'Захват'):
            self.main.navigation_frame.next_button.configure(state = 'disabled')
            self.main.navigation_frame.prev_button.configure(state = 'disabled')
        elif (self.get() == 'Обработка'):
            self.main.navigation_frame.next_button.configure(state = 'normal')
            self.main.navigation_frame.prev_button.configure(state = 'normal')



class App(ctk.CTk):    
    def __init__(self):
        super().__init__()

        
        self.title("mjolnir")
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        height = int(0.8*screen_height)
        width = int(0.8*screen_width)
        self.geometry(f"{width}x{height}")

        self.image_path="D:\Photonics\KGW МУР\!18_d.tif"

        self.cam = camera.initCamera()
        
        self.image = 0
        

        self.setupGrid()
        
        self.menu = TitleMenu(self)
        self.menu.grid()

        self.navigation_frame = NavigationFrame(self)
        self.navigation_frame.grid(row=1, column=0, rowspan = 1, sticky="nsew")
        
        self.right_frame = RightFrame(self, camera_handle = self.cam)
        self.right_frame.grid(row=0, column=1, rowspan = 2, sticky="nsew")
        
        self.left_frame = LeftFrame(self, right_frame_handle= self.right_frame, image_path=self.image_path)
        self.left_frame.grid(row=0, column=0, rowspan = 1, sticky="nsew")




        
        self.update_idletasks()
        self.mainloop()
    
    def setupGrid(self):
        self.grid_columnconfigure(0, weight=2)  
        self.grid_columnconfigure(1, weight=1)  
        self.grid_rowconfigure(0, weight=1)     
        self.grid_rowconfigure(1, weight = 0)



class TitleMenu(CTkTitleMenu):
    def __init__(self, master):
        super().__init__(master)

        file_button = self.add_cascade("Файл")

        dropdown1 = CustomDropdownMenu(widget=file_button)

        open_sub_menu = dropdown1.add_submenu("Открыть")
        open_sub_menu.add_option(option="Файл", command = self.openFile)
        open_sub_menu.add_option(option="Папку")

        dropdown1.add_separator()

        save_sub_menu = dropdown1.add_submenu("Экспортировать")
        save_sub_menu.add_option(option = "Данные текущего изображения")
        save_sub_menu.add_option(option = "Данные всех изображений")

    def openFile(self):
        file_path = filedialog.askopenfilename(filetypes = [("tif file(*.tif)","*.tif")], defaultextension = [("tif file(*.tif)","*.tif")])
        if file_path:
            try:
                self.image = Image.open(file_path)
                self.master.image  = self.image
            except Exception as e:
                print("Error during image import")

# Example usage
if __name__ == "__main__":
    app = App()

    # # Configure the grid for the main application window
    # self.grid_columnconfigure(0, weight=2)  # Left frame is 2 times wider
    # self.grid_columnconfigure(1, weight=1)  # Right frame is 1 time wider
    # self.grid_rowconfigure(0, weight=1)     # Single row for the frames

    # # Create the left frame
    # left_frame = LeftFrame(app, image_path="D:\Photonics\KGW МУР\!18_d.tif")
    # left_frame.grid(row=0, column=0, sticky="nsew")

    # # Create the right frame
    # right_frame = RightFrame(app)
    # right_frame.grid(row=0, column=1, sticky="nsew")

    # # Ensure the frames resize correctly
    # self.update_idletasks()  # Force an update to ensure the grid configuration is applied immediately

    # # Debugging: Print frame sizes after 1 second
    # def print_frame_sizes():
    #     print(f"Left frame width: {left_frame.winfo_width()}")
    #     print(f"Right frame width: {right_frame.winfo_width()}")

    # self.after(1000, print_frame_sizes)

    # self.mainloop()