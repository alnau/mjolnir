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

import os

import utility as util

import tkinter as tk
from  tkinter import filedialog

import image_processing as ip

from CTkMenuBar import *

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class NavigationFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.image_index = 0
        # self.right_frame_handle = right_frame_handle

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", pady=10, padx = const.DEFAULT_PADX, side = 'top')
        self.button_frame.grid_columnconfigure(0, weight=3)
        self.button_frame.grid_columnconfigure(1, weight=3)
        
        self.prev_button = ctk.CTkButton(self.button_frame, text="<", 
                                        command = lambda: self.switch('back'))
        self.prev_button.grid(row = 0, column = 0, sticky = 'e', padx = const.DEFAULT_PADX, pady = 5)
        # self.button1.pack(side="left", padx=10, pady=5)

        self.next_button = ctk.CTkButton(self.button_frame, text=">", 
                                        command = lambda: self.switch("fwd"))
        self.next_button.grid(row = 0, column = 1, sticky = 'w', padx = const.DEFAULT_PADX, pady = 5)
        # self.button2.pack(side="right", padx=10, pady=5)

    # посылает сигнал о переключении картинок
    def switch(self, btn):
        if (btn == 'fwd'):
            self.image_index = min(self.image_index+1, len(self.master.image_data_container) - 1)
        else:
            self.image_index = max(0, self.image_index - 1)
        name = ''
        if (len(self.master.image_data_container)!= 0):
            name = self.master.image_data_container[self.image_index].image_name
        self.master.right_frame.entry.configure(placeholder_text = name)
        self.master.right_frame.updatePlotAfterAnalysis(self.image_index)
        self.master.right_frame.updatePrintedDataAfterAnalysis(self.image_index)
        self.master.left_frame.loadImage(self.master.image_data_container[self.image_index].norm_image, name = self.master.image_data_container[self.image_index].image_name)





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

        self.p0_real_coords = (0,0)
        self.p1_real_coords = (0,0)


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

    def reset(self):
        self.start_coords = (0,0)
        self.tmp_coords = (0,0)
        self.end_coords = (0,0)

        self.p0_real_coords = (0,0)
        self.p1_real_coords = (0,0)

        self.clearPhoto()


    def drawLines(self, event):
        if (self.master.right_frame.photo_is_captured or self.master.right_frame.tabview.get() == 'Обработка'):
            if (event.type == '4'):
                index = self.master.navigation_frame.image_index
                self.master.image_data_container[index].image_has_been_analysed = False
                self.master.image_data_container[index].optimisation_needed = False
                self.master.right_frame.clearPlot()
                tabview_handle = self.master.right_frame.tabview 
                tabview_handle.check_var.set('on')
                self.tmp_coords = (0,0)
                self.start_coords = (event.x, event.y)
                tabview_handle.analyse_all_button.configure(state = 'normal')
                tabview_handle.analyse_current_button.configure(state = 'normal')
                self.clearPhoto()
                
            elif (event.type == '5'):
                self.end_coords = (event.x, event.y)
                self.tmp_coords = self.end_coords
                self.p0_real_coords = (int(self.start_coords[0]*self.image.width/self.image_resized.width), int(self.start_coords[1]*self.image.height/self.image_resized.height))
                self.p1_real_coords = (int(self.end_coords[0]*self.image.width/self.image_resized.width), int(self.end_coords[1]*self.image.height/self.image_resized.height))
                self.right_frame_handle.updatePlot(self.p0_real_coords, self.p1_real_coords)
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


    def updateLineOnPhoto(self):
        # TODO добавить флаг конца обработки и снимать его в случае, если пользователь изменил линию
        tmp_image = self.image_resized.copy()

        draw = ImageDraw.Draw(tmp_image)

        line_color = (255)  
        line_width = 2  # Width of the line
        circle_radius = 2
        draw.ellipse(util.getCircleBound(self.start_coords, circle_radius), fill = line_color, width = line_width)
        draw.ellipse(util.getCircleBound(self.tmp_coords, circle_radius), fill = line_color, width = line_width)
        draw.line([self.start_coords, self.tmp_coords], fill = line_color, width = line_width)
        return tmp_image
    
    def clearPhoto(self):
        tmp_image = self.image_resized.copy()

        photo = ImageTk.PhotoImage(tmp_image)

        # Update the label with the resized image
        self.image_canvas.config(width=tmp_image.width, height=tmp_image.height)
        self.image_canvas.image = photo
        self.image_canvas.create_image(0,0,image=photo,anchor = 'nw')


    def loadImage(self, image, name = ''):
        width = self.winfo_width()
        height = self.winfo_height()

        self.image_resized = image.resize((width, height))
        self.photo = ImageTk.PhotoImage(self.image_resized)

        self.image_canvas.config(width=self.image_resized.width, height=self.image_resized.height)
        self.image_canvas.image = self.photo
        self.image_canvas.create_image(0,0,image=self.photo,anchor = 'nw')
        index = self.master.navigation_frame.image_index
        self.master.right_frame.entry.configure(placeholder_text = name)
        text = str(index + 1) + "/" + str(len(self.master.image_data_container))
        self.L = ctk.CTkLabel(self.image_canvas, text = text, fg_color = 'transparent', width = 20, text_color = 'black')
        self.L.place(x = 10,y = 10, anchor = 'nw')

    def switchImage(self, index):
        idata = self.master.image_data_container[index]
        name = ''
        if (idata != 'None'):
            name = idata.image_name
        self.loadImage(idata.modified_image, name)

    def resize_image(self, event):
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
        self.image = Image.open("D:\Photonics\KGW МУР\!18_o.tif").convert('L')

        self.plot_width = 5
        self.plot_height = 3
        
        self.fig, self.ax = plt.subplots(figsize=(self.plot_width, self.plot_height))  
        # self.ax.plot([1, 2, 3], [4, 5, 6])
        # self.ax.text(self.plot_width/2, self.plot_height/2, 'Нет данных'
        #             ,horizontalalignment='center', verticalalignment='center', transform = self.ax.transAxes)
        self.ax.set_aspect('auto', adjustable='box')

        # Create a canvas to embed the plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="x", padx = const.DEFAULT_PADX, pady = (5,0), side = "top")

        # Add an entry field just under the plot
        self.entry_frame = ctk.CTkFrame(self, )
        self.entry_frame.pack(fill="x", pady=(10, 5), side = 'top')
        
        self.entry = ctk.CTkEntry(self.entry_frame)
        self.entry.pack(fill="x", side = 'left', padx=5, pady=2, expand = True)
        
        # TODO необходимо подгружать имена текущих файлов в entry
        self.capture_button = ctk.CTkButton(self.entry_frame, text = 'Захватить', command= self.captureImage)
        self.capture_button.pack(side = 'left', pady = 2, padx = const.DEFAULT_PADX)
    


        # Add a thin frame just under the entry field
        self.thin_frame = ctk.CTkFrame(self, height=2, bg_color="gray")
        self.thin_frame.pack(fill="x", padx =10, pady=5,)

        # self.empty_frame = ctk.CTkFrame(self, fg_color='transparent')
        # self.empty_frame.pack(fill="x", expand = True)

        self.tabview = Tab(master = self, main=master)
        self.tabview.pack(side = 'top', fill = 'x') 
        
        self.continue_button = ctk.CTkButton(master = self, command = self.nextImage, text = 'Продолжить', state = 'disabled')
        self.continue_button.pack(side = 'top', fill = 'x')

        self.status_frame = ctk.CTkFrame(self, )
        self.status_frame.pack(fill="x", padx = 2, side = 'top', expand = True)

        self.status = ctk.CTkLabel(self.status_frame, text = '', height = master.navigation_frame.winfo_height())   
        self.status.pack( fill = 'x', pady = const.DEFAULT_PADX, side = 'top')

    def logStatus(self, text_to_log):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        new_text = current_time + ": " + text_to_log
        self.status.configure(text = new_text, text_color = 'red')
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
            # TODO: заменить image на данные с камеры, а также заблокировать запись пока не будет установлено имя
            
            self.master.left_frame.loadImage(self.image)
            self.image_data = ip.ImageData(self.image)

            self.capture_button.configure(text = 'Отмена')
            self.photo_is_captured = True

            self.continue_button.configure(state = 'enabled')
        

    def nextImage(self):
        if len(self.entry.get()) != 0:
            # TODO запись данных, возобновление трансляции
            self.master.left_frame.clearPhoto()
            if (self.tabview.check_var.get() == 'on'):
                self.image_data.optimisation_needed = False
            

            self.tabview.check_var.set('off')

            self.master.image_data_container.append(self.image_data)
            self.logStatus('Данные записаны')

            self.capture_button.configure(text = 'Захватить')
            self.photo_is_captured = False
            self.master.left_frame.reset()
            self.continue_button.configure(state = 'disabled')
        else:
            self.logStatus('Введите название файла')

    def clearPlot(self):
        self.ax.clear()
        self.canvas.draw()

    def updatePlot(self, p0, p1): 

        self.image_data.p0_initial = p0
        self.image_data.p1_initial = p1
        coords, brightness = util.getBrightness(p0, p1,self.image)
        self.ax.clear()
        self.ax.plot(coords, brightness)
        self.canvas.draw()

    def updateWindowAfterAnalysis(self):
        self.after(100, self.tabview.configure(state = 'normal'))
        index = self.master.navigation_frame.image_index
        self.updatePlotAfterAnalysis(index)
        self.updatePrintedDataAfterAnalysis(index)
        self.master.left_frame.switchImage(index)
        self.tabview.analyse_all_button.configure(state = 'disabled')
        self.tabview.analyse_current_button.configure(state = 'disabled')


    def updatePlotAfterAnalysis(self, index):
        idata = self.master.image_data_container[index]

        self.ax.clear()
    
        self.ax.plot(idata.coord, idata.normalised_brightness_values)
        self.canvas.draw()

    def updatePrintedDataAfterAnalysis(self, index):
        pass


class Tab(ctk.CTkTabview):
    def __init__(self, master, main, **kwargs):
        super().__init__(master, **kwargs)

        self.main = main

        self.configure(command = self.lockNavigation)

        self.pack(fill="x", expand = True)

        #################   Захват   #########################

        self.capture_tab = self.add("Захват")  
          
        self.slider_frame = ctk.CTkFrame(self.capture_tab, fg_color='transparent')
        self.slider_frame.pack(fill = 'x', side = 'top')

        self.slider_label = ctk.CTkLabel(self.slider_frame, text='Экспозиция    ')
        self.slider_label.pack(side = 'left')
        self.slider = ctk.CTkSlider(self.slider_frame, from_ = 0,to = const.MAX_EXPOSURE_MS, command = self.sliderEvent)
        self.slider.pack(fill = 'x', side = 'left', expand = True) 

        self.option_frame = ctk.CTkFrame(self.capture_tab, fg_color='transparent')
        self.option_frame.pack(side = 'top', fill = 'x', pady = (10,0))
        
    
        self.check_var = ctk.StringVar(value="off")
        self.select_optimisation_button = ctk.CTkCheckBox(self.option_frame, onvalue= 'on', offvalue = 'off', variable= self.check_var, text = 'Использовать пользовательскую линию для анализа')
        self.select_optimisation_button.grid(sticky = 'nw')

        #################     Обработка   #########################
        self.analyse_tab = self.add("Обработка")

        self.analysis_frame = ctk.CTkFrame(self.analyse_tab)
        self.analysis_frame.pack(fill = 'x', side = 'top')
        self.analysis_frame.grid_columnconfigure((0,1), weight = 1)

        self.analyse_all_button = ctk.CTkButton(self.analysis_frame, text = 'Обработать все', command=self.analyseAll)
        self.analyse_all_button.grid(row = 0, column = 1, sticky = 'ew', padx = const.DEFAULT_PADX)
        self.analyse_current_button = ctk.CTkButton(self.analysis_frame, text = 'Обработать текущий', command=self.analyseCurrent)
        self.analyse_current_button.grid(row = 0, column = 0, sticky = 'ew', padx = const.DEFAULT_PADX)

        self.lockNavigation()

    def analyseAll(self):
        self.configure(state = 'disabled')
        threading.Thread(target=self.analyseAllWorker, args=(), daemon=True).start()

    def analyseCurrent(self):
        self.configure(state = 'disabled')
        threading.Thread(target=self.analyseCurrentWorker, args=(), daemon=True).start()


    def analyseAllWorker(self):
        
        # все изображения прошли базовую обработку и имеют полный набор данных (хотелось бы верить)
        # self.analyse_button.configure(state = 'disabled')
    
        for image_data in self.main.image_data_container:
            image_data.analyseImage()
            name = image_data.image_name
            image_data.image_has_been_analysed = True
            
            text = "Обработка " + name + " закончена"
            self.after(100, self.master.logStatus(text))
        
        self.master.updateWindowAfterAnalysis()


    def analyseCurrentWorker(self):
        
        index = self.main.navigation_frame.image_index
        self.main.image_data_container[index].analyseImage()
        name = self.main.image_data_container[index].image_name
        self.main.image_data_container[index].image_has_been_analysed = True

        text = "Обработка " + name + " закончена"
        self.after(100, self.master.logStatus(text))
        
        self.master.updateWindowAfterAnalysis()
    

    def sliderEvent(self, val):
        try:
            camera.setExposure(camera=self.main.cam, exposure_time_ms = val)
        except:
            print('Error. cannot set exposure')
        
        image_array = np.array(self.master.image)
        brightest_pixel_value = np.max(image_array)

        self.slider.configure(button_color = const.FG_COLOR , progress_color= const.PROGRESS_COLOR, button_hover_color = const.HOVER_COLOR)
        self.master.capture_button.configure(state = 'normal', fg_color = const.FG_COLOR)
        if (brightest_pixel_value == 255):
            self.master.capture_button.configure(state = 'disabled', fg_color = 'red')
            self.slider.configure(button_color = 'red', button_hover_color = 'red', progress_color = 'red' )
            


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

        
        self.image_data_container = []

        self.title("mjolnir")
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        height = int(0.8*screen_height)
        width = int(0.8*screen_width)
        self.geometry(f"{width}x{height}")

        self.image_path="D:\Photonics\KGW МУР\!18_o.tif"

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
        open_sub_menu.add_option(option="Папку", command = self.openFolder)

        dropdown1.add_separator()

        save_sub_menu = dropdown1.add_submenu("Экспортировать")
        save_sub_menu.add_option(option = "Данные текущего изображения", command = self.saveFile)
        save_sub_menu.add_option(option = "Данные всех изображений", command = self.saveAll)

    def openFile(self):
        file_path = filedialog.askopenfilename(filetypes = [("tif file(*.tif)","*.tif")], defaultextension = [("tif file(*.tif)","*.tif")])
        if file_path:
            try:
                _, tail= os.path.split(file_path)
                plotname, _ = os.path.splitext(tail)
                image = Image.open(file_path)
                pure_name,_ = os.path.splitext(plotname)
                self.image_data_container.append(ip.ImageData(image, pure_name))
            except Exception as e:
                print("Error during image import")

    def openFolder(self):
        self.master.image_data_container = []
        dir_path = filedialog.askdirectory()
        if dir_path:          
            names = []
            for image_name in os.listdir(dir_path):
                if (image_name.endswith(".tif")):
                    names.append(image_name)
            for name in names:
                image = Image.open(os.path.join(dir_path, name)).convert('L')
                pure_name,_ = os.path.splitext(name)
                self.master.image_data_container.append(ip.ImageData(image, pure_name))
            
            self.master.left_frame.loadImage(self.master.image_data_container[0].norm_image, names[0])
            text = "Импортировано " + str(len(self.master.image_data_container)) + " изображений. Вы можете приступиить к их обработке"
            self.master.right_frame.logStatus(text)
            self.master.right_frame.tabview.set('Обработка')
            self.master.navigation_frame.next_button.configure(state = 'normal')
            self.master.navigation_frame.prev_button.configure(state = 'normal')

    def saveFile(self):
        index = self.mastr.navigation_frame.image_index
        image_data = self.master.image_data_container[index]
        image_data.plotBepis()
        
        self.right_frame.logStatus("Данные", image_data.image_name, "сохранены в папке mjolnir")
                        
    def saveAll(self):
        for image_data in self.master.image_data_container:
            image_data.plotBepis()
            
        self.right_frame.logStatus("Данные измерений сохранены в папке mjolnir")




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