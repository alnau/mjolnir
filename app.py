import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import numpy as np
from PIL import ImageDraw

from camera_feed import Camera

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
        

    def toggleControl(self):
        pass

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
            
            self.master.image_frame.loadImage(self.master.image_data_container[0].norm_image, names[0])
            text = "Импортировано " + str(len(self.master.image_data_container)) + " изображений. Вы можете приступиить к их обработке"
            self.master.right_frame.logMessage(text)
            self.master.right_frame.tabview.set('Обработка')
            self.master.navigation_frame.next_button.configure(state = 'normal')
            self.master.navigation_frame.prev_button.configure(state = 'normal')

    def saveFile(self):
        index = self.mastr.navigation_frame.image_index
        image_data = self.master.image_data_container[index]
        image_data.plotBepis()
        
        self.right_frame.logMessage("Данные", image_data.image_name, "сохранены в папке mjolnir")
                        
    def saveAll(self):
        for image_data in self.master.image_data_container:
            image_data.plotBepis()
            
        self.right_frame.logMessage("Данные измерений сохранены в папке mjolnir")



class NavigationFrame(ctk.CTkFrame):
    def __init__(self, master, camera_handle, **kwargs):
        super().__init__(master, **kwargs)

        self.image_index = 0
        # self.right_frame_handle = right_frame_handle

        self.is_active = True
        # self.cam = camera_handle

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
        self.master.image_frame.loadImage(self.master.image_data_container[self.image_index].norm_image, name = self.master.image_data_container[self.image_index].image_name)

    def toggleControl(self):
        # if self.is_active:
        #     self.prev_button.configure(state = 'disabled')
        #     self.next_button.configure(state = 'disabled')
        #     self.is_active = False
        # else:
        #     self.prev_button.configure(state = 'normal')
        #     self.next_button.configure(state = 'normal')
        #     self.is_active = True
        pass





class imageFrame(ctk.CTkFrame):
    def __init__(self, master, right_frame_handle, camera_handle, **kwargs):
        super().__init__(master, **kwargs)

        self.right_frame_handle = right_frame_handle

        self.start_coords = (0,0)
        self.tmp_coords = (0,0)
        self.end_coords = (0,0)

        # Если True останавливает обновление картинки с камеры
        self.is_pause = True

        self.p0_real_coords = (0,0)
        self.p1_real_coords = (0,0)

        self.man_we_just_switched_to_new_image = False


        self.start_dialog = ctk.CTkFrame(self)
        self.start_dialog.pack(fill="both", padx = (5,0), pady = 5, expand=True)


        self.start_dialog.grid_columnconfigure(0, weight = 3)
        self.start_dialog.grid_columnconfigure(1, weight = 1)
        self.start_dialog.grid_columnconfigure(2, weight = 3)

        self.start_dialog.grid_rowconfigure(0, weight = 3)
        self.start_dialog.grid_rowconfigure(1, weight = 1)
        self.start_dialog.grid_rowconfigure(2, weight = 3)

        self.start_button = ctk.CTkButton(self.start_dialog, text='Включить камеру', command = self.activateCamera)
        self.start_button.grid(row = 1,column = 1, sticky = 'we')


        self.image_canvas = tk.Canvas(self, highlightbackground="black")
        # self.image_canvas.pack(fill="both", padx = (5,0), pady = 5, expand=True)

        
        # self.bind("<Configure>", self.resize_image)

        # Bind the <Configure> event to resize the image
        
        self.image_canvas.bind("<ButtonPress-1>", self.drawLines )
        self.image_canvas.bind("<B1-Motion>", self.drawLines )
        self.image_canvas.bind("<ButtonRelease-1>", self.drawLines )
        self.image_canvas.bind("<ButtonRelease-1>", self.drawLines )



    def toggleControl(self):
        pass
    
    def startVideoFeed(self):
        self.is_pause = False
        update_image_thread = threading.Thread(target = self.startVideoFeedWorker, args = (self.master.camera_feed_image,))
        update_image_thread.daemon = True
        update_image_thread.start()

    def startVideofeedWorker(self):
        # while (self.master.cam.is_open() and not self.is_pause):
        try:
            while (not self.is_pause):
                if (self.master.cam.wait_for_frame()):
                    #ждем пока прийдет новое изображение
                    self.updateCanvas(self.master.camera_feed_image)
                    time.sleep(0.08)
        except: 
            print('Goddamn, I''m running out of creative ideas of how to handle exept''s associated with camera')
    def activateCamera(self):
        self.start_dialog.pack_forget()
        # self.image_canvas = tk.Canvas(self)
        self.image_canvas.pack(fill="both", padx = (5,0), pady = 5, expand=True)
        # self.image = Image.open(self.image_path)
        self.bind("<Configure>", self.resize_image)
        self.resize_image(None)
        self.master.toggleControl()

        self.master.initCamera()
        
        self.resize_image(None)

    def reset(self):
        self.start_coords = (0,0)
        self.tmp_coords = (0,0)
        self.end_coords = (0,0)

        self.p0_real_coords = (0,0)
        self.p1_real_coords = (0,0)

        self.clearPhoto()
        self.man_we_just_switched_to_new_image  = True


    def drawLines(self, event):
        if (self.master.right_frame.photo_is_captured or self.master.right_frame.tabview.get() == 'Обработка'):
            index = self.master.navigation_frame.image_index
            if (event.type == '4'):
                # TODO тут какая-то полная грязь с логикой. Я уже слишком пьян чтобы разобраться в этом дерьме
                # фактически ифы ниже только для того, чтобы нормально отрабатывала логика сброса галки о том, 
                # что оптимизация не нужна. Уверен, на трезвую голову ты справишься куда лучше
                # 
                # При этом, все работает
                if (self.man_we_just_switched_to_new_image):
                    self.man_we_just_switched_to_new_image = False
                elif(len(self.master.image_data_container) != 0):
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
                self.p0_real_coords = (int(self.start_coords[0]*self.master.current_image.width/self.image_resized.width), int(self.start_coords[1]*self.master.current_image.height/self.image_resized.height))
                self.p1_real_coords = (int(self.end_coords[0]*self.master.current_image.width/self.image_resized.width), int(self.end_coords[1]*self.master.current_image.height/self.image_resized.height))
                self.right_frame_handle.updatePlot(self.p0_real_coords, self.p1_real_coords)
            elif (event.type == '6'):
                self.tmp_coords = (event.x, event.y)
            if (self.tmp_coords != (0,0)):
                updated_image = self.updateLineOnPhoto()
                
                photo = ImageTk.PhotoImage(updated_image)

                self.image_canvas.config(width=updated_image.width, height=updated_image.height)
                self.image_canvas.image = photo
                self.image_canvas.create_image(0,0,image=photo,anchor = 'nw')
        else:
            self.master.right_frame.logMessage("Необходимо сначала захватить изображение")

    
    def getCrossLineCoord(self, point, is_rising):
            ret = 0
            if (is_rising):
                # /
                p0 = (point[0]-const.CROSS_HALF_HEIGHT, point[1] + const.CROSS_HALF_HEIGHT)
                p1 = (point[0]+const.CROSS_HALF_HEIGHT, point[1] - const.CROSS_HALF_HEIGHT)
                ret = [p0,p1]
            else:
                #\
                p0 = (point[0]-const.CROSS_HALF_HEIGHT, point[1] - const.CROSS_HALF_HEIGHT)
                p1 = (point[0]+const.CROSS_HALF_HEIGHT, point[1] + const.CROSS_HALF_HEIGHT)
                ret = [p0,p1]
            return ret      


    def updateCanvas(self, shared_image):
        if 'image' in shared_image:
            img = shared_image['image']
            resized_img = img.resize((self.winfo_width(), self.winfo_height()), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(resized_img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo  # Keep a reference to avoid garbage collection
        self.canvas.after(100, self.updateCanvas, shared_image)  # 10 Hz refresh rate


    def updateLineOnPhoto(self):
        # TODO добавить флаг конца обработки и снимать его в случае, если пользователь изменил линию
        # ВАЖНО: выглядит так, что я уже пофиксил это. Взгляни более трезвым взглядом
        tmp_image = self.image_resized.copy()

        self.draw = ImageDraw.Draw(tmp_image)

        self.draw.ellipse(util.getCircleBound(self.start_coords, const.CIRCLE_RADIUS), fill = const.LINE_COLOR, width = const.LINE_WIDTH)
        self.draw.ellipse(util.getCircleBound(self.tmp_coords, const.CIRCLE_RADIUS), fill = const.LINE_COLOR, width = const.LINE_WIDTH)
        self.draw.line([self.start_coords, self.tmp_coords], fill = const.LINE_COLOR, width = const.LINE_WIDTH)
        if (self.master.right_frame.tabview.needed_active_pos_monitoring):
            print("well, we are here")
            point = self.master.right_frame.tabview.p0
            print(self.getCrossLineCoord(point,True))
            self.draw.line(self.getCrossLineCoord(point,True), fill = const.LINE_COLOR, width = const.LINE_WIDTH)
            self.draw.line(self.getCrossLineCoord(point,False), fill = const.LINE_COLOR, width = const.LINE_WIDTH)
        return tmp_image
    
    def callForDrawRefresh(self):
        updated_image = self.updateLineOnPhoto()
                
        photo = ImageTk.PhotoImage(updated_image)

        self.image_canvas.config(width=updated_image.width, height=updated_image.height)
        self.image_canvas.image = photo
        self.image_canvas.create_image(0,0,image=photo,anchor = 'nw')

    def clearPhoto(self):
        tmp_image = self.image_resized.copy()

        photo = ImageTk.PhotoImage(tmp_image)

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
        text = str(index + 1) + "/" + str(len(self.master.image_data_container)+1)
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
        image = self.master.current_image
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
        # self.image = Image.open("D:\Photonics\KGW МУР\!18_o.tif").convert('L')

        self.plot_width = 5
        self.plot_height = 3

        self.is_active = True

        # self.cam = camera_handle
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
        self.entry.pack(fill="x", side = 'left', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY, expand = True)
        self.entry.focus()
        
        # TODO необходимо подгружать имена текущих файлов в entry
        # ВАЖНО: Точно работает с "захваченными" кадрами, загруженные не проверял. Возможно, с ними факап 
        self.capture_button = ctk.CTkButton(self.entry_frame, text = 'Захватить', command= self.captureImage)
        self.capture_button.pack(side = 'left', pady = const.DEFAULT_PADY, padx = const.DEFAULT_PADX)
    


        # Add a thin frame just under the entry field
        self.thin_frame = ctk.CTkFrame(self, height=2, bg_color="gray")
        self.thin_frame.pack(fill="x", padx =10, pady=5,)

        # self.empty_frame = ctk.CTkFrame(self, fg_color='transparent')
        # self.empty_frame.pack(fill="x", expand = True)

        self.tabview = Tab(master = self, camera_handle=camera_handle, main=master)
        self.tabview.pack(side = 'top', fill = 'x') 
        
        self.continue_button = ctk.CTkButton(master = self, command = self.nextImage, text = 'Продолжить', state = 'disabled')
        self.continue_button.pack(side = 'top', fill = 'x')

        self.status_frame = ctk.CTkFrame(self, )
        self.status_frame.pack(fill="x", padx = 2, side = 'top', expand = True)

        self.status = ctk.CTkLabel(self.status_frame, text = '', height = master.navigation_frame.winfo_height())   
        self.status.pack( fill = 'x', pady = const.DEFAULT_PADX, side = 'top')

    def toggleControl(self):
        if self.is_active:
            self.capture_button.configure(state = 'disabled')
            self.tabview.configure(state = 'disabled')
            self.is_active = False
        else:
            self.capture_button.configure(state = 'normal')
            self.tabview.configure(state = 'normal')
            self.is_active = True

    def logMessage(self, text_to_log):
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


    def lockCamera(self):
        self.master.updateImage()
        
        self.master.image_frame.is_pause = True
        self.capture_button.configure(text = 'Отмена')
        self.continue_button.configure(state = 'enabled')
        self.master.image_frame.image_canvas.configure(highlightbackground="red")
        self.photo_is_captured = True
        self.master.image_frame.loadImage(self.master.current_image)

        self.logMessage('Фото захвачено')

    def unlockCamera(self):
        self.master.image_frame.is_pause = False
        self.capture_button.configure(text = 'Захватить')
        self.continue_button.configure(state = 'disabled')
        self.master.image_frame.image_canvas.configure(highlightbackground="black")
        self.photo_is_captured = False
        self.master.image_frame.clearPhoto()
        

    def captureImage(self):
        # отработка захвата или сброса текущего изображения
        
        if (self.photo_is_captured):
            # переход к живой камере
            self.unlockCamera()
            self.logMessage('Фото сброшено')
        elif(len(self.entry.get())!=0) :
            # Показать картинку, сохранить в буффер
            self.lockCamera()
            self.image_data = ip.ImageData(self.master.current_image, self.entry.get())
        else:
                self.logMessage('Введите имя файла')

        

    def nextImage(self):
        if len(self.entry.get()) != 0:

            self.unlockCamera()

            # TODO запись данных, возобновление трансляции
            # ВАЖНО если работает класс Camera, то уже решено
            if (self.tabview.check_var.get() == 'on'):
                self.image_data.optimisation_needed = False
            
            self.tabview.check_var.set('off')
            self.entry.focus()

            self.master.image_data_container.append(self.image_data)
            self.master.navigation_frame.image_index += 1
            
            self.logMessage('Данные записаны')
            self.entry.delete(0, 'end')


            self.master.image_frame.reset()
        else:
            self.logMessage('Введите название файла')

    def clearPlot(self):
        self.ax.clear()
        self.canvas.draw()

    def updatePlot(self, p0, p1): 

        self.image_data.p0_initial = p0
        self.image_data.p1_initial = p1
        coords, brightness = util.getBrightness(p0, p1,self.master.current_image)
        self.ax.clear()
        self.ax.plot(coords, brightness)
        self.canvas.draw()

    # TODO крашится как минимум начиная с этого момента. Вроде, не сильно драматично, но просто не оч
    # TODO кстати, после анализа графики переключаются, но не отрисовываются линии, вдоль которых 
    # проводился анализ. Должно быть что-то простое (или банально не реализованное). 
    # Займись этим
    def updateWindowAfterAnalysis(self):
        try:
            self.after(100, self.tabview.configure(state = 'normal'))
            index = self.master.navigation_frame.image_index
            self.updatePlotAfterAnalysis(index)
            self.updatePrintedDataAfterAnalysis(index)
            self.master.image_frame.switchImage(index)
            self.tabview.analyse_all_button.configure(state = 'disabled')
            self.tabview.analyse_current_button.configure(state = 'disabled')
        except:
            print('You know, I''m just hanging around, anyways, checkout updateWidndowAfterAnalysis()')

    def updatePlotAfterAnalysis(self, index):
        idata = self.master.image_data_container[index]

        self.ax.clear()
    
        self.ax.plot(idata.coord, idata.normalized_brightness_values)
        self.canvas.draw()

    def updatePrintedDataAfterAnalysis(self, index):
        pass


class Tab(ctk.CTkTabview):
    def __init__(self, master, camera_handle, main, **kwargs):
        super().__init__(master, **kwargs)

        self.main = main
        # self.cam = camera_handle
        self.configure(command = self.handleTab)

        self.pack(fill="x", expand = True)

        self.p0 = (100,100)
        self.p1 = (0,0)

        self.angle_sec = -1

        self.needed_active_pos_monitoring = False

        self.firstImage = 0
        self.secondImage = 0

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

        #################     Обработка   #########################
        self.analyse_tab = self.add("Клиновидность")

        self.base_entry_frame = ctk.CTkFrame(self.analyse_tab, )
        self.base_entry_frame.pack(fill="x", pady=(10, 5), side = 'top')
        
        self.base_label = ctk.CTkLabel(self.base_entry_frame, text = 'База (см)')
        self.base_label.pack(side = 'left', pady = const.DEFAULT_PADY, padx = const.DEFAULT_PADX)
        
        self.base_entry = ctk.CTkEntry(self.base_entry_frame, )
        self.base_entry.pack(fill="x", side = 'left', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY, expand = True)
        
        self.base_entry.insert(0, str(const.DEFAULT_BASE_CM))

        self.parallelism_button_frame = ctk.CTkFrame(self.analyse_tab)
        self.parallelism_button_frame.pack(fill = 'x', side = 'top')
        self.parallelism_button_frame.grid_columnconfigure((0,1), weight = 1)

        self.first_button = ctk.CTkButton(self.parallelism_button_frame, text = 'Записать первую точку', command=self.setFirstPosition)
        self.first_button.grid(row = 0, column = 0, sticky = 'ew', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY)
        
        self.second_button = ctk.CTkButton(self.parallelism_button_frame, text = 'Записать вторую точку', command=self.setSecondPosition)
        self.second_button.grid(row = 0, column = 1, sticky = 'ew', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY)

        res = self.getParallelismReport((0,0), (0,0), 0)
        self.resultsLabel = []
        for i in range(3):
            self.resultsLabel.append(ctk.CTkLabel(self.analyse_tab, text = res[i], anchor= 'nw'))
            self.resultsLabel[i].pack(fill = 'x', expand = True, side = 'top', pady = 2)
            self.resultsLabel[i].cget("font").configure(size=15)

        self.handleTab()


    def resetReport(self):
        res = self.getParallelismReport((0,0), (0,0), 0)
        for i in range(3):
            self.resultsLabel[i].configure(text = res[i])        

    def getParallelismReport(self, p0, p1, angle):
        p0x = round(p0[0])
        p0y = round(p0[1])
        p1x = round(p1[0])
        p1y = round(p1[1])
        
        text1 = 'Координата первой точки: (' + str(p0x) +', ' + str(p0y) + ') px\n'
        text2 = 'Координата второй точки: (' + str(p1x) +', ' + str(p1y) + ') px\n'
        text3 = 'Угол клиновидности: ' + str(round(angle,0)) + '"'
        return [text1,text2,text3]


    # TODO: вероятно, не самый "умный" подход к названию, путается с handle, которые передаются от родительского класса
    def handleTab(self):
        if (self.get() == 'Захват'):
            self.main.navigation_frame.next_button.configure(state = 'disabled')
            self.main.navigation_frame.prev_button.configure(state = 'disabled')
            # self.p0 = (0,0)
            self.p1 = (0,0)
        elif (self.get() == 'Обработка'):
            self.main.navigation_frame.next_button.configure(state = 'normal')
            self.main.navigation_frame.prev_button.configure(state = 'normal')
            # self.p0 = (0,0)
            self.p1 = (0,0)
        elif (self.get() == 'Клиновидность'):
            self.resetReport()

    def calculateAngleSec(self):
        dist_px  = np.sqrt((self.p0[0]-self.p1[0])**2 + (self.p0[1]-self.p1[1])**2)
        dist_mm = const.PIXEL_TO_MM*dist_px
        base_mm = float(self.base_entry.get())*100

        angle_rad = dist_mm/base_mm/(const.KGW_REFRACTION_INDEX-1)
        angle_sec = angle_rad*180/np.pi/60/60 
        return angle_sec
        
    def angleCalculationWorker(self):
        while True:
            # TODO: пока закомментил
            # if (self.needed_active_pos_monitoring):
            #     self.p1 = util.getCOM(self.main.getImage())
            #     self.angle_sec = self.calculateAngleSec()

            #     res = self.getParallelismReport(self.p0, self.p1, self.angle_sec)
            #     for i in range(3):
            #         self.resultsLabel[i].configure(text = res[i])
            #     self.main.image_frame.callForDrawRefresh()
            time.sleep(0.2)

    def setFirstPosition(self):
        self.firstImage = self.main.getImage()
        # self.p0 = util.getCOM(self.firstImage)
        self.needed_active_pos_monitoring = True
    
        self.angle_sec = self.calculateAngleSec()
        # self.getParallelismReport(self.p0, self.p1, self.angle_sec)
        
        res = self.getParallelismReport(self.p0, self.p1, self.angle_sec)
        for i in range(3):
            self.resultsLabel[i].configure(text = res[i])

        threading.Thread(target=self.angleCalculationWorker, args=(), daemon=True).start()



    def setSecondPosition(self):
        self.secondImage = self.main.getImage()
        self.p1 = util.getCOM(self.secondImage)

        self.needed_active_pos_monitoring = False
        self.angle_sec = self.calculateAngleSec()
        res = self.getParallelismReport(self.p0, self.p1, self.angle_sec)
        for i in range(3):
            self.resultsLabel[i].configure(text = res[i])


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
            self.after(100, self.master.logMessage(text))
        
        # TODO возникает какая-то сложная проблема с выходом за пределы массиве в функции, в которой нет массивов 
        # (см todo ~ 516)
        self.master.updateWindowAfterAnalysis()


    def analyseCurrentWorker(self):
        
        index = self.main.navigation_frame.image_index
        self.main.image_data_container[index].analyseImage()
        name = self.main.image_data_container[index].image_name
        self.main.image_data_container[index].image_has_been_analysed = True

        text = "Обработка " + name + " закончена"
        self.after(100, self.master.logMessage(text))
        
        self.master.updateWindowAfterAnalysis()
    

    def sliderEvent(self, val):
        try:
            self.main.cam.setExposure(exposure_time_ms = val)
        except:
            print('Error. cannot set exposure')
            self.master.logMessage('Ошибка, не  могу установить экспозицию')
        
        image_array = np.array(self.master.image)
        brightest_pixel_value = np.max(image_array)

        self.slider.configure(button_color = const.FG_COLOR , progress_color= const.PROGRESS_COLOR, button_hover_color = const.HOVER_COLOR)
        self.master.capture_button.configure(state = 'normal', fg_color = const.FG_COLOR)
        if (brightest_pixel_value == 255):
            self.master.capture_button.configure(state = 'disabled', fg_color = 'red')
            self.slider.configure(button_color = 'red', button_hover_color = 'red', progress_color = 'red' )
            





class App(ctk.CTk):    
    def __init__(self):
        super().__init__()

        
        self.image_data_container = []

        self.title("mjolnir")

        self.cam = Camera()
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        height = int(0.8*screen_height)
        width = int(0.8*screen_width)
        self.geometry(f"{width}x{height}")

        # TODO Эти три строчки являются банальной заглушкой
        self.image_path="D:\Photonics\KGW МУР\!18_o.tif"        
        self.camera_feed_image = Image.open(self.image_path).convert('L')
        self.current_image = self.camera_feed_image

        self.setupGrid()
        
        self.menu = TitleMenu(self)
        self.menu.grid()

        self.navigation_frame = NavigationFrame(self, camera_handle = self.cam)
        self.navigation_frame.grid(row=1, column=0, rowspan = 1, sticky="nsew")
        
        self.right_frame = RightFrame(self, camera_handle = self.cam)
        self.right_frame.grid(row=0, column=1, rowspan = 2, sticky="nsew")
        
        self.image_frame = imageFrame(self, right_frame_handle= self.right_frame,camera_handle = self.cam)
        self.image_frame.grid(row=0, column=0, rowspan = 1, sticky="nsew")

        self.widget_list = [self.menu, self.navigation_frame, self.right_frame, self.image_frame]

        self.toggleControl()

        
        self.update_idletasks()
        self.mainloop()

    def initCamera(self):
        # По идее, начиная отсюда у нас заработает камера 
        try:
            camera_thread = threading.Thread(target=self.cam.cameraFeed, args=(self.camera_feed_image,))
            camera_thread.daemon = True  # Daemonize the thread to stop it when the main program exits
            camera_thread.start()
        except:
            print('I fucking hate working without physical camera attached to my dying laptop')
            print('If this error occured on stable version of mjolnir (stable? Heh, nevermind), please check out App.initCamera()')
            print('Of course I have no ideas of what had I done to cause this shitshow in the first place')
 

    def toggleControl(self):
        for widget in self.widget_list:
            widget.toggleControl()

    def setupGrid(self):
        self.grid_columnconfigure(0, weight=2)  
        self.grid_columnconfigure(1, weight=1)  
        self.grid_rowconfigure(0, weight=1)     
        self.grid_rowconfigure(1, weight = 0)
    
    def getImage(self):
        return self.camera_feed_image

    def updateImage(self):
        self.current_image = self.getImage()






# Example usage
if __name__ == "__main__":
    app = App()

    # # Configure the grid for the main application window
    # self.grid_columnconfigure(0, weight=2)  # Left frame is 2 times wider
    # self.grid_columnconfigure(1, weight=1)  # Right frame is 1 time wider
    # self.grid_rowconfigure(0, weight=1)     # Single row for the frames

    # # Create the left frame
    # image_frame = imageFrame(app, image_path="D:\Photonics\KGW МУР\!18_d.tif")
    # image_frame.grid(row=0, column=0, sticky="nsew")

    # # Create the right frame
    # right_frame = RightFrame(app)
    # right_frame.grid(row=0, column=1, sticky="nsew")

    # # Ensure the frames resize correctly
    # self.update_idletasks()  # Force an update to ensure the grid configuration is applied immediately

    # # Debugging: Print frame sizes after 1 second
    # def print_frame_sizes():
    #     print(f"Left frame width: {image_frame.winfo_width()}")
    #     print(f"Right frame width: {right_frame.winfo_width()}")

    # self.after(1000, print_frame_sizes)

    # self.mainloop()