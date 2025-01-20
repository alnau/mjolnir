import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk,ImageDraw
import numpy as np
import threading
import time
from datetime import datetime

import customtkinter as ctk
import tkinter as tk
from  tkinter import filedialog
from CTkMenuBar import *
import CTkMessagebox as msg
import os
import logging


# import error as e
import camera_feed_thorlabs as thor
from camera_feed_thorlabs import ThorCamera
import camera_feed_generic as gen
from camera_feed_generic import GenericCamera
import constants as const
import utility as util
import image_processing as ip



ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("dark-blue")  

class TitleMenu(CTkTitleMenu):
    def __init__(self, master, folders_names):
        super().__init__(master)

        self.backup_folders = folders_names
        self.data_is_external = False
        file_button = self.add_cascade("Файл")
        reopen_camera_buttom = self.add_cascade("Изменить камеру", command = self.master.initUI)
        
        file_dropdown = CustomDropdownMenu(widget=file_button)

        open_sub_menu = file_dropdown.add_submenu("Открыть")
        open_sub_menu.add_option(option="Файл", command = self.openFile)
        open_sub_menu.add_option(option="Папку", command = self.openFolder)

        recover_sub_menu  = file_dropdown.add_submenu("Восстановить сессию")

        for folder in self.backup_folders:
            recover_sub_menu.add_option(option = folder, command = lambda: self.recoverFromFolder(folder))


        file_dropdown.add_separator()

        save_sub_menu = file_dropdown.add_submenu("Экспортировать")
        save_sub_menu.add_option(option = "Данные текущего изображения", command = self.saveFile)
        save_sub_menu.add_option(option = "Данные всех изображений", command = self.saveAll)
     


        self.exterminate_button = self.add_cascade("DoW")
        self.exterminate_button.configure(state = 'disabled')

        geno_dropdown = CustomDropdownMenu(widget=self.exterminate_button)
        geno_dropdown.add_option(option = "NUKE EM, OPPIE!", command = self.master.initUI)
        geno_dropdown.add_option(option = "SHOOT YOUR OWN FOOT!", command = self.shotYourself)

        self.master.bind("<Control-Up>", self.onControl_UpPress)
        self.master.bind("<Control_L>", self.onControlPress)
        
        
        # self.bind("<ControlRelease>", self.onCtrlRelease)
    
    def onControlPress(self, event):
        self.exterminate_button.configure(state = 'disabled')

    def onControl_UpPress(self,event):
        print('CTRL')
        self.exterminate_button.configure(state = 'normal')
        # self.master.after(1000, self.exterminate_button.configure(state = 'disabled'))


    def shotYourself(self):

        try: 
            a = 1/0
        except Exception as e:
            # Логируем исключение
            logging.error("Leg had been shot successfully:", str(e))
            print("Leg had been shot successfully:", str(e))


    def recoverFromFolder(self, folder_name):
        dir_path = util.resourcePath(self.master.base_path + folder_name)
        print(dir_path)
        names = []
        self.master.image_data_container = []

        for image_name in os.listdir(dir_path):
            if (image_name.endswith('.tif')):
                names.append(image_name)
        for name in names:
            image = Image.open(os.path.join(dir_path, name)).convert('L')
            pure_name,_ = os.path.splitext(name)
            pure_name.removesuffix('.tif')
            self.master.image_data_container.append(ip.ImageData(image, pure_name))

        # TODO: здесь ломается подгрузка: архивные изображения высвечиваются, но сменяются на дефолтную заглушку. Ожидаю что openFile и openFolder будут иметь ту-же проблему. Разберись на трезвую голову
        self.master.image_frame.loadImage(self.master.image_data_container[0].norm_image, names[0])
        text = "Восстановлено " + str(len(self.master.image_data_container)) + " изображений. Вы можете продолжить работу"
        self.master.right_frame.logMessage(text)
        self.master.right_frame.tabview.set('Обработка')
        self.master.navigation_frame.next_button.configure(state = 'normal')
        self.master.navigation_frame.prev_button.configure(state = 'normal')
        self.master.image_frame.is_pause = True
        self.data_is_external = True

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
                self.data_is_external = True
            except Exception as e:
            # Логируем исключение
                logging.error("Error during image import", str(e))
                print("Error during image import;:", str(e))

    def openFolder(self):
        self.master.right_frame.logMessage('Начат импорт файлов...')
        self.master.image_data_container = []
        dir_path = filedialog.askdirectory()
        if dir_path:          
            names = []
            for image_name in os.listdir(dir_path):
                if (image_name.endswith('.tif')):
                    names.append(image_name)
            for name in names:
                image = Image.open(os.path.join(dir_path, name)).convert('L')
                pure_name,_ = os.path.splitext(name)
                pure_name.removesuffix('.tif')
                self.master.image_data_container.append(ip.ImageData(image, pure_name))
            
            self.master.image_frame.loadImage(self.master.image_data_container[0].norm_image, names[0])
            text = "Импортировано " + str(len(self.master.image_data_container)) + " изображений. Вы можете приступить к их обработке"
            self.master.right_frame.logMessage(text)
            self.master.right_frame.tabview.set('Обработка')
            self.master.navigation_frame.next_button.configure(state = 'normal')
            self.master.navigation_frame.prev_button.configure(state = 'normal')
            self.data_is_external = True

    def saveFile(self, path = ''):
        index = self.master.navigation_frame.image_index
        image_data = self.master.image_data_container[index]
        image_data.plotBepis(path)
        
        self.master.right_frame.logMessage("Данные", image_data.image_name, "сохранены в папке")
                        
    def saveAll(self, path =''):
        dir_path = filedialog.askdirectory(title='Выберете папку для сохранения файлов')
        saving_thread = threading.Thread(target=self.saveAllWorker, args=(dir_path,))
        saving_thread.daemon = True 
        saving_thread.start()
        
    def saveAllWorker(self, path):
        new_names = []
        width_data_d = []
        width_data_o = []
        for image_data in self.master.image_data_container:
            image_data.plotBepis(path)

            r_ref = 0
            if (image_data.plotname!='control'):
                number, test_for_d_o = image_data.plotname.rsplit("_",1)
                if (test_for_d_o == "d"):
                    width_data_d.append(round(2*image_data.radius_mm, 2))
                    new_names.append(number)
                elif (test_for_d_o == "o"):
                    width_data_o.append(round(2*image_data.radius_mm,2))
            elif (image_data.plotname == 'control'):
                r_ref = round(2*image_data.radius_mm,2)

        print("------------------")

        if (len(new_names)!=len(width_data_d) or len(new_names)!=len(width_data_o) ):
            print("error with files")

        util.printReportToXLSX(new_names, width_data_d, width_data_o, r_ref, path)  
        path_printout = '/lastResults'
        if (path != ''):
            path_printout = path           
        self.master.right_frame.logMessage("Данные измерений сохранены в папке " + str(path_printout))
        self.master.files_are_unsaved = False



class NavigationFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.image_index = 0
        self.is_active = True

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", pady=10, padx = const.DEFAULT_PADX, side = 'top')
        self.button_frame.grid_columnconfigure(0, weight=3)
        self.button_frame.grid_columnconfigure(1, weight=3)
        
        self.prev_button = ctk.CTkButton(self.button_frame, text="<", 
                                        command = lambda: self.switch('back'))
        self.prev_button.grid(row = 0, column = 0, sticky = 'e', padx = const.DEFAULT_PADX, pady = 5)


        self.next_button = ctk.CTkButton(self.button_frame, text=">", 
                                        command = lambda: self.switch("fwd"))
        self.next_button.grid(row = 0, column = 1, sticky = 'w', padx = const.DEFAULT_PADX, pady = 5)

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
        self.master.image_frame.switchImage(self.image_index)
        # self.master.right_frame.updateWindowAfterAnalysis()
        self.master.image_frame.reset()



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
    def __init__(self, master, right_frame_handle, **kwargs):
        super().__init__(master, **kwargs)

        self.cam = 0
        self.right_frame_handle = right_frame_handle

        self.start_coords = (0,0)
        self.tmp_coords = (0,0)
        self.end_coords = (0,0)

        # Если True останавливает обновление картинки с камеры
        # self.is_pause = False

        self.p0_real_coords = (0,0)
        self.p1_real_coords = (0,0)

        self.man_we_just_switched_to_new_image = False

        self.start_dialog = ctk.CTkFrame(self)
        self.start_dialog.pack(fill="both", padx = (5,0), pady = 5, expand=True)

        self.start_dialog.grid_columnconfigure((0,3), weight = 3)
        self.start_dialog.grid_columnconfigure((1,2), weight = 1)

        self.start_dialog.grid_rowconfigure((0,3), weight = 3)
        self.start_dialog.grid_rowconfigure((1,2), weight = 1)

        self.camera_list = self.getCameraList()
        self.camera_selection = ctk.CTkComboBox(self.start_dialog, values = self.camera_list, command = self.chooseCamera)
        self.camera_selection.set('Камера...')
        self.camera_selection.grid(row  =1, column = 1, padx = const.DEFAULT_PADX, sticky ='we')
        
        self.start_button = ctk.CTkButton(self.start_dialog, text='Включить камеру', command = self.activateCamera, state = 'disabled')
        self.start_button.grid(row = 1,column = 2, padx = const.DEFAULT_PADY, sticky = 'we')


        self.image_canvas = tk.Canvas(self, highlightbackground="black")
        
        self.image_canvas.bind("<ButtonPress-1>", self.drawLines )
        self.image_canvas.bind("<B1-Motion>", self.drawLines )
        self.image_canvas.bind("<ButtonRelease-1>", self.drawLines )
        self.image_canvas.bind("<ButtonRelease-1>", self.drawLines )

    def getCameraList(self):
        tmp_camera_list = []
        if (thor.isCameraConnected()):
            tmp_camera_list.append("ThorCam")
        for i in range(10):
            if (gen.isCameraConnected(i)):
                text = 'USB - камера ' + str(i) 
                tmp_camera_list.append(text)

        return tmp_camera_list
    
    def chooseCamera(self, choise):
        if (choise == 'ThorCam'):
            self.cam = ThorCamera()
            self.start_button.configure(state = 'normal')
        elif(choise[:-2] == 'USB - камера'):
            index = int(choise[-1])
            self.cam = GenericCamera(index)
            self.start_button.configure(state = 'normal')
        
    def toggleControl(self):
        pass

    def startCameraFeed(self):
        # По идее, начиная отсюда у нас заработает камера 
        self.master.is_pause = False
        camera_thread = threading.Thread(target=self.cameraFeedWorker, args=())
        camera_thread.daemon = True 
        # Дадим паузу в 2с чтобы интерфейс адаптировался к изображению с камеры
        self.master.after(2000, camera_thread.start)
    
    def cameraFeedWorker(self):

        while True:
            # запросим последнее изображение с камеры и загрузим его в app.camera_feed_image
            self.cam.cameraFeed(master_app=self) 
            # подменим app.current_image TODO: возможно, безопаснее будет засунуть это под else до update_canvas
            self.master.updateImage()
            if (self.master.is_pause or self.master.right_frame.tabview.needed_active_pos_monitoring):
                # Если изображение захвачено (is_pause == True) или мы измеряем клиновидность, отключить автоообновление
                # картинки с камеры
                pass
            else:
                self.updateCanvas(self.master.current_image)
                self.master.right_frame.tabview.checkForOverexposure()
            time.sleep(0.05)

    # вызываетя после выбора камеры. Убивает диалоговое окно с выбором и переключает на живую 
    # трансляцию
    def activateCamera(self):
        self.start_dialog.pack_forget()
        self.image_canvas.pack(fill="both", padx = (5,0), pady = 5, expand=True)
        self.bind("<Configure>", self.resizeImage)
        self.resizeImage(None)
        self.master.toggleControl()
        self.resizeImage(None)
        self.master.right_frame.tabview.slider.set(self.cam.getExposureFrac()) 
        self.master.right_frame.tabview.slider2.set(self.cam.getExposureFrac()) 
        
        # self.startVideoFeed()
        self.startCameraFeed()

    # обновляет данные при переходе к новому изображению
    def reset(self):
        self.start_coords = (0,0)
        self.tmp_coords = (0,0)
        self.end_coords = (0,0)

        self.p0_real_coords = (0,0)
        self.p1_real_coords = (0,0)

        self.clearPhoto()
        self.man_we_just_switched_to_new_image  = True


    def drawLines(self, event):

        if (self.master.right_frame.tabview.get() != "Захват"):
            self.master.right_frame.logMessage("Это должно быть возможно, но временно функционал ограничен")

        else:
            if (self.master.right_frame.photo_is_captured or self.master.right_frame.tabview.get() == 'Обработка'):
                index = self.master.navigation_frame.image_index
                if (event.type == '4'):
                    # тут какая-то полная грязь с логикой. Я уже слишком пьян чтобы разобраться в этом дерьме
                    # фактически ифы ниже только для того, чтобы нормально отрабатывала логика сброса галки о том, 
                    # что оптимизация не нужна. Уверен, на трезвую голову ты справишься куда лучше
                    # 
                    # При этом, все работает
                    if (self.man_we_just_switched_to_new_image):
                        self.man_we_just_switched_to_new_image = False
                    elif(len(self.master.image_data_container) != 0):
                            print(index)
                            self.master.image_data_container[index].image_has_been_analysed = False
                            self.master.image_data_container[index].optimisation_needed = True
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
                    self.image_canvas.create_image(0,0,image=photo,anchor = 'nw')
                    self.image_canvas.image = photo
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
                # \
                p0 = (point[0]-const.CROSS_HALF_HEIGHT, point[1] - const.CROSS_HALF_HEIGHT)
                p1 = (point[0]+const.CROSS_HALF_HEIGHT, point[1] + const.CROSS_HALF_HEIGHT)
                ret = [p0,p1]
            return ret      


    def updateCanvas(self, shared_image):

        img = shared_image.copy()
        self.image_resized = img.resize((self.winfo_width(), self.winfo_height()), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(self.image_resized)
        self.image_canvas.config(width=self.image_resized.width, height=self.image_resized.height)

        # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        self.image_canvas.create_image(0,0,image=photo,anchor = 'nw')
        self.image_canvas.image = photo
        
   
    def updateLineOnPhoto(self):
        tmp_image = self.image_resized.copy()

        self.draw = ImageDraw.Draw(tmp_image)

        self.draw.ellipse(util.getCircleBound(self.start_coords, const.CIRCLE_RADIUS), fill = const.LINE_COLOR, width = const.LINE_WIDTH)
        self.draw.ellipse(util.getCircleBound(self.tmp_coords, const.CIRCLE_RADIUS), fill = const.LINE_COLOR, width = const.LINE_WIDTH)
        self.draw.line([self.start_coords, self.tmp_coords], fill = const.LINE_COLOR, width = const.LINE_WIDTH)
        if (self.master.right_frame.tabview.needed_active_pos_monitoring):
            point = self.master.right_frame.tabview.p0
            self.draw.line(self.getCrossLineCoord(point,True), fill = const.LINE_COLOR, width = const.LINE_WIDTH)
            self.draw.line(self.getCrossLineCoord(point,False), fill = const.LINE_COLOR, width = const.LINE_WIDTH)
        return tmp_image
    
    def callForCrossesRefresh(self):
        width = self.winfo_width()
        height = self.winfo_height()

        master_image = self.master.getImage().copy()
        tmp_image = master_image.copy()
        tmp_image = tmp_image.resize((width,height))

        self.draw = ImageDraw.Draw(tmp_image)
        # Взможно здесь следует временно выводить изображение как RGB, чтобы выделить точку цветом
        if (self.master.right_frame.tabview.needed_active_pos_monitoring):
            point = self.master.right_frame.tabview.p0
            point = (point[0]*self.master.crop_factor_x, point[1]*self.master.crop_factor_y)
            self.draw.line(self.getCrossLineCoord(point,True), fill = const.LINE_COLOR, width = const.LINE_WIDTH)
            self.draw.line(self.getCrossLineCoord(point,False), fill = const.LINE_COLOR, width = const.LINE_WIDTH)
                
        photo = ImageTk.PhotoImage(tmp_image)

        self.image_canvas.config(width=tmp_image.width, height=tmp_image.height)
        self.image_canvas.create_image(0,0,image=photo,anchor = 'nw')
        self.image_canvas.image = photo


    def clearPhoto(self):
        tmp_image = self.image_resized.copy()

        photo = ImageTk.PhotoImage(tmp_image)

        self.image_canvas.config(width=tmp_image.width, height=tmp_image.height)
        self.image_canvas.create_image(0,0,image=photo,anchor = 'nw')
        self.image_canvas.image = photo


    def loadImage(self, image, name = ''):
        width = self.winfo_width()
        height = self.winfo_height()

        self.image_resized = image.resize((width, height))
        self.photo = ImageTk.PhotoImage(self.image_resized)

        self.image_canvas.config(width=self.image_resized.width, height=self.image_resized.height)
        self.image_canvas.create_image(0,0,image=self.photo,anchor = 'nw')
        self.image_canvas.image = self.photo
        
        index = self.master.navigation_frame.image_index
        self.master.right_frame.entry.configure(placeholder_text = name)
        text = str(index + 1) 
        self.L = ctk.CTkLabel(self.image_canvas, text = text, fg_color = 'transparent', width = 20, text_color = 'black')
        self.L.place(x = 10,y = 10, anchor = 'nw')


    def switchImage(self, index):
        idata = self.master.image_data_container[index]
        name = ''
        if (idata != 'None'):
            name = idata.image_name
        if (idata.image_has_been_analysed):
            self.loadImage(idata.modified_image, name)
        else:
            self.loadImage(idata.norm_image, name)

    def resizeImage(self, event):
        width = self.winfo_width()
        height = self.winfo_height()

        # загрузим изображение, отмасштабируем и конвертируем его
        image = self.master.current_image
        self.image_resized = image.resize((width, height))
        self.photo = ImageTk.PhotoImage(self.image_resized)

        # обновим холст
        self.image_canvas.config(width=self.image_resized.width, height=self.image_resized.height)
        self.image_canvas.create_image(0,0,image=self.photo,anchor = 'nw')
        self.image_canvas.image = self.photo
        
        # ... и данные по кропу
        self.master.crop_factor_x = width/self.master.current_image.width
        self.master.crop_factor_y = height/self.master.current_image.height

class RightFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.photo_is_captured = False

        self.plot_width = 4.5
        self.plot_height = 2.7

        self.is_active = True


        self.fig, self.ax = plt.subplots(figsize=(self.plot_width, self.plot_height))  
        self.ax.set_aspect('auto', adjustable='box')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="x", padx = const.DEFAULT_PADX, pady = (5,0), side = "top")

        self.entry_frame = ctk.CTkFrame(self, )
        self.entry_frame.pack(fill="x", pady=(10, 5), side = 'top')
        
        self.entry = ctk.CTkEntry(self.entry_frame)
        self.entry.pack(fill="x", side = 'left', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY, expand = True)
        self.entry.focus()
        
        self.capture_button = ctk.CTkButton(self.entry_frame, text = 'Захватить', command= self.captureImage)
        self.capture_button.pack(side = 'left', pady = const.DEFAULT_PADY, padx = const.DEFAULT_PADX)
        self.master.bind('<Return>', self.captureImageOnEnter)
    
        self.thin_frame = ctk.CTkFrame(self, height=2, bg_color="gray")
        self.thin_frame.pack(fill="x", padx =10, pady=5,)

        self.tabview = Tab(master = self, main=master)
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
            color = f'#{r:02x}{g:02x}{b:02x}'  
            self.status.configure( text_color=color)  
            time.sleep(0.05) 


    def lockCamera(self):
        self.master.updateImage()
        
        self.master.is_pause = True
        self.capture_button.configure(text = 'Отмена')
        self.continue_button.configure(state = 'normal')
        self.master.image_frame.image_canvas.configure(highlightbackground="red")
        self.photo_is_captured = True
        self.master.image_frame.loadImage(self.master.current_image)

        self.logMessage('Фото захвачено')

    def unlockCamera(self):
        self.master.is_pause = False
        self.capture_button.configure(text = 'Захватить')
        self.continue_button.configure(state = 'disabled')
        self.master.image_frame.image_canvas.configure(highlightbackground="black")
        self.photo_is_captured = False
        self.master.image_frame.clearPhoto()
    
    def captureImageOnEnter(self, event):
        if (self.tabview.get() == 'Захват'):
            self.captureImage()

    def captureImage(self):
        # отработка захвата или сброса текущего изображения
        
        if (self.photo_is_captured):
            # переход к живой камере
            self.unlockCamera()
            self.logMessage('Фото сброшено')
            # чисто на всякий пожарный снимем все возможные триггеры на пропуск оптимизации 
            self.master.image_frame.start_coords = (0,0)
            self.master.image_frame.end_coords = (0,0)
            self.tabview.check_var.set('off')
        elif(len(self.entry.get())!=0) :
            # Показать картинку, сохранить в буффер
            self.lockCamera()
            self.image_data = ip.ImageData(self.master.current_image, self.entry.get())
        else:
            self.logMessage('Введите имя файла')

        

    def nextImage(self):
        if len(self.entry.get()) != 0:

            self.unlockCamera()

            if (self.tabview.check_var.get() == 'on'):
                self.image_data.optimisation_needed = False
                self.image_data.line_was_built = True
                self.image_data.p0_im_space = self.master.image_frame.start_coords
                self.image_data.p1_im_space = self.master.image_frame.end_coords

                crop_x = self.master.crop_factor_x
                crop_y = self.master.crop_factor_y
                p0_true = (self.master.image_frame.start_coords[0]/crop_x, self.master.image_frame.start_coords[1]/crop_y)
                p1_true = (self.master.image_frame.end_coords[0]/crop_x, self.master.image_frame.end_coords[1]/crop_y)

                self.image_data.p0_new = p0_true
                self.image_data.p1_new = p1_true
            
            
            self.tabview.check_var.set('off')
            self.entry.focus()
            self.image_data.p0_new = self.master.image_frame.p0_real_coords
            self.image_data.p1_new = self.master.image_frame.p1_real_coords

            self.image_data.p0_im_space = self.master.image_frame.start_coords
            self.image_data.p1_im_space = self.master.image_frame.end_coords
            self.master.image_data_container.append(self.image_data)
 
            self.master.navigation_frame.image_index += 1
            

            file_name = self.entry.get() + '.tif'
            self.image_data.initial_image.save(os.path.join(self.master.backup_path, file_name))

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

    # def updateWidowOnSwitch(self):
    #     self.after(100, self.tabview.configure(state = 'normal'))
    #     index = self.master.navigation_frame.image_index
    #     self.updatePlotAfterAnalysis(index)
    #     self.updatePrintedDataAfterAnalysis(index)
    #     self.master.image_frame.switchImage(index)

    def updateWindowAfterAnalysis(self):
        # try:
        self.after(100, self.tabview.configure(state = 'normal'))
        index = self.master.navigation_frame.image_index
        self.updatePlotAfterAnalysis(index)
        self.updatePrintedDataAfterAnalysis(index)
        self.master.image_frame.switchImage(index)
        self.tabview.analyse_all_button.configure(state = 'disabled')
        self.tabview.analyse_current_button.configure(state = 'disabled')
        # except:
        #     print('You know, I''m just hanging around, anyways, checkout updateWidndowAfterAnalysis()')

    def updatePlotAfterAnalysis(self, index):
        idata = self.master.image_data_container[index]

        self.ax.clear()
    
        self.ax.plot(idata.coord, idata.normalized_brightness_values)
        self.canvas.draw()

    def updatePrintedDataAfterAnalysis(self, index):
        self.tabview.displayReport()


class Tab(ctk.CTkTabview):
    def __init__(self, master, main, **kwargs):
        super().__init__(master, **kwargs)

        self.main = main

        self.configure(command = self.tabHandler)

        self.pack(fill="x", expand = True)

        self.p0 = (100,100)
        self.p1 = (0,0)

        self.angle_sec = 0

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

        self.max_exposure_label = ctk.CTkLabel(self.slider_frame, text = '')
        self.max_exposure_label.pack(side = 'left')

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
        self.analysis_frame.grid_rowconfigure(0, weight = 0)
        self.analysis_frame.grid_rowconfigure(1, weight = 2)


        self.analyse_all_button = ctk.CTkButton(self.analysis_frame, text = 'Обработать все', command=self.analyseAll)
        self.analyse_all_button.grid(row = 0, column = 1, sticky = 'ew', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY)
        self.analyse_current_button = ctk.CTkButton(self.analysis_frame, text = 'Обработать текущий', command=self.analyseCurrent)
        self.analyse_current_button.grid(row = 0, column = 0, sticky = 'ew', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY)

        self.report_textbox = ctk.CTkTextbox(self.analysis_frame)
        self.report_textbox.insert('0.0', 'Данные не обработаны')
        self.report_textbox.configure(state = 'disabled')
        self.report_textbox.grid(row = 1, column = 0, columnspan = 2, sticky = 'new', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY)

        #################   Клиновидность   #########################
        self.parallelism_tab = self.add("Клиновидность")

        self.slider_frame2 = ctk.CTkFrame(self.parallelism_tab, fg_color='transparent')
        self.slider_frame2.pack(fill = 'x', side = 'top')


        self.slider_label2 = ctk.CTkLabel(self.slider_frame2, text='Экспозиция    ')
        self.slider_label2.pack(side = 'left')
        self.slider2 = ctk.CTkSlider(self.slider_frame2, from_ = 0,to = const.MAX_EXPOSURE_MS, command = self.sliderEvent)
        self.slider2.pack(fill = 'x', side = 'left', expand = True) 

        self.max_exposure_label2 = ctk.CTkLabel(self.slider_frame2, text = '')
        self.max_exposure_label.pack(side = 'left')
        
        self.base_entry_frame = ctk.CTkFrame(self.parallelism_tab, )
        self.base_entry_frame.pack(fill="x", pady=(10, 5), side = 'top')
        
        self.base_label = ctk.CTkLabel(self.base_entry_frame, text = 'База (см)')
        self.base_label.pack(side = 'left', pady = const.DEFAULT_PADY, padx = const.DEFAULT_PADX)
        
        self.base_var = ctk.StringVar(self.main,value = str(const.DEFAULT_BASE_CM))
        self.base_entry = ctk.CTkEntry(self.base_entry_frame, textvariable=self.base_var)
        self.base_entry.pack(fill="x", side = 'left', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY, expand = True)
        self.base_var.trace_add('write', self.updateBase)

        # self.base_entry.insert(0, str(const.DEFAULT_BASE_CM))

        self.first_button = ctk.CTkButton(self.parallelism_tab, text = 'Записать первую точку', command=self.setFirstPosition)
        self.first_button.pack(fill = 'x', side = 'top')
        

        res = self.getParallelismReport()
        self.resultsLabel = ctk.CTkLabel(self.parallelism_tab, text =res , anchor= 'n')
        self.resultsLabel.pack(fill = 'x', expand = True, side = 'top', pady = 2)
        self.resultsLabel.cget("font").configure(size=45)

        self.tabHandler()

    def updateBase(self,var,index,mode):
        new_base = self.base_var.get()
        if (new_base!=''):
            const.DEFAULT_BASE_CM = int(new_base)
            util.updateIni('default_base_cm', new_base)


    def displayReport(self):
        data_was_analysed = False
        index = 0
        tmp_image_data = 0
        try:
            index = self.main.navigation_frame.image_index
            tmp_image_data = self.main.image_data_container[index]
            data_was_analysed = tmp_image_data.radius_was_calculated
        except Exception as e:
            
            logging.error("well, no luck on report printout side. Possibly, there is nothing inside image_data_container;", str(e))
            print("well, no luck on report printout side. Possibly, there is nothing inside image_data_container;", str(e))

            if (tmp_image_data == 0):
                print('Yeah, just checked, seems like it. Try to find workaround, godspeed')
                logging.error('Yeah, just checked, seems like it. Try to find workaround, godspeed')
        
        self.report_textbox.configure(state = 'normal')
        self.report_textbox.delete('0.0', 'end')
        if (data_was_analysed and self.get() == 'Обработка'):
            report_text = tmp_image_data.report
            self.report_textbox.insert('0.0', report_text)
        else:
            self.report_textbox.insert('0.0', 'Данные не обработаны')
        self.report_textbox.configure(state = 'disabled')
     


    def tabHandler(self):
        if (self.get() == 'Захват'):
            self.main.is_pause = False
            self.needed_active_pos_monitoring = False
            self.main.navigation_frame.next_button.configure(state = 'disabled')
            self.main.navigation_frame.prev_button.configure(state = 'disabled')
            self.p1 = (0,0)
        elif (self.get() == 'Обработка'):
            self.needed_active_pos_monitoring = False
            self.main.is_pause = True
            self.main.navigation_frame.next_button.configure(state = 'normal')
            self.main.navigation_frame.prev_button.configure(state = 'normal')
            self.p1 = (0,0)
            self.displayReport()
        elif (self.get() == 'Клиновидность'):
            self.main.is_pause = False
            self.angle_sec = 0

    def calculateAngleSec(self):
        dist_px  = np.sqrt((self.p0[0]-self.p1[0])**2 + (self.p0[1]-self.p1[1])**2)
        dist_mm = const.PIXEL_TO_MM*dist_px
        base_mm = float(self.base_entry.get())*10

        angle_rad = np.arctan(dist_mm/2/base_mm)/(const.KGW_REFRACTION_INDEX-1)
        angle_sec = angle_rad*180/np.pi*60*60 
        return angle_sec
    
    def getParallelismReport(self):
        return str(self.angle_sec) + '"'
        
    def angleCalculationWorker(self):
        while True:
            if (self.needed_active_pos_monitoring):
                self.p1 = util.getCOM(self.main.getImage())
                self.angle_sec = self.calculateAngleSec()

                res = self.getParallelismReport()

                self.resultsLabel.configure(text = res)
                self.main.image_frame.callForCrossesRefresh()
            time.sleep(0.2)

    def setFirstPosition(self):
        self.firstImage = self.main.getImage()
        self.p0 = util.getCOM(self.firstImage)
        self.needed_active_pos_monitoring = True
    
        self.angle_sec = self.calculateAngleSec()
        # self.getParallelismReport(self.p0, self.p1, self.angle_sec)
        
        res = self.getParallelismReport()
        self.resultsLabel.configure(text = res)

        threading.Thread(target=self.angleCalculationWorker, args=(), daemon=True).start()




    def analyseAll(self):
        self.configure(state = 'disabled')
        threading.Thread(target=self.analyseAllWorker, args=(), daemon=True).start()

    def analyseCurrent(self):
        self.configure(state = 'disabled')
        threading.Thread(target=self.analyseCurrentWorker, args=(), daemon=True).start()

    # TODO: Добавить бегущий статус-бар при обработке (возможно, при любом вызове analyseImage)
    def analyseAllWorker(self):
        
        # Костыль, который закрывает баг в nextImage: для начала обработки
        # надо сначала зафиксировать последнее изображение (nextImage), 
        # при этом к индексу картинки автоматически прибавляется 1, 
        # пусть даже следующее изображение не захватывается
        self.main.navigation_frame.image_index = max(0, self.main.navigation_frame.image_index-1)
        
        # все изображения прошли базовую обработку и имеют полный набор данных (хотелось бы верить)
        # self.analyse_button.configure(state = 'disabled')
        self.master.logMessage("Обработка начата...")
        for image_data in self.main.image_data_container:
            image_data.analyseImage()
            name = image_data.image_name
            image_data.image_has_been_analysed = True
            
            text = "Обработка " + name + " закончена"
            self.after(100, self.master.logMessage(text))
        
        self.main.is_pause = True
        self.after(1000, self.master.logMessage("Все изображения обработаны"))
        self.master.updateWindowAfterAnalysis()
        self.main.files_are_unsaved = True



    def analyseCurrentWorker(self):
        
        index = self.main.navigation_frame.image_index
        self.main.image_data_container[index].analyseImage()
        name = self.main.image_data_container[index].image_name
        self.main.image_data_container[index].image_has_been_analysed = True

        text = "Обработка " + name + " закончена"
        self.after(100, self.master.logMessage(text))
        self.main.is_pause = True
        
        self.master.updateWindowAfterAnalysis()
    
    def sliderEvent(self, val):
        
        
        self.main.image_frame.cam.setExposure(exposure_time_ms = val)

        self.checkForOverexposure()

    def checkForOverexposure(self):
        image_array = np.array(self.main.current_image)
        brightest_pixel_value = np.max(image_array)

        self.max_exposure_label2.configure(text = brightest_pixel_value)
        self.max_exposure_label.configure(text = brightest_pixel_value)

        if (brightest_pixel_value < 250):
            self.slider.configure(button_color = const.FG_COLOR , progress_color= const.PROGRESS_COLOR, button_hover_color = const.HOVER_COLOR)
            self.slider2.configure(button_color = const.FG_COLOR , progress_color= const.PROGRESS_COLOR, button_hover_color = const.HOVER_COLOR)
            
            self.master.capture_button.configure(state = 'normal', fg_color = const.FG_COLOR)
            return False
        else:
            self.master.capture_button.configure(state = 'disabled', fg_color = 'red')
            self.slider.configure(button_color = 'red', button_hover_color = 'red', progress_color = 'red' )
            self.slider2.configure(button_color = 'red', button_hover_color = 'red', progress_color = 'red' )
            
            return True


class App(ctk.CTk):    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.initUI()
        
    def initUI(self):
        self.image_data_container = []

        self.title("mjolnir")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        height = int(0.8*screen_height)
        width = int(0.8*screen_width)
        self.geometry(f"{width}x{height}")

        # TODO Изменить заглушку
        try:
            self.image_path= util.resourcePath('mockup1.tif')        
            self.camera_feed_image = Image.open(self.image_path).convert('L')
        except:
            # arr = np.arange(0, screen_width*screen_height, 1, np.uint8)
            arr = np.zeros(1024*1536)
            arr = np.reshape(arr, (1536,1024))
            self.camera_feed_image = Image.fromarray(arr).convert('L')
            

        self.current_image = self.camera_feed_image
        

        self.base_path = util.resourcePath('tmp/')
        current_date = util.getCurrentDateStr() 
        self.backup_path = self.base_path + current_date + '_tmp/'
        self.organizeBackup() 
        self.backup_folders_names = util.getBackupFoldersNames(self.base_path)
        self.crop_factor_x = 0
        self.crop_factor_y = 0

        self.files_are_unsaved = False

        self.is_pause = False

        self.setupGrid()

        self.menu = TitleMenu(self, folders_names= self.backup_folders_names)
        self.menu.grid()

        self.navigation_frame = NavigationFrame(self)
        self.navigation_frame.grid(row=1, column=0, rowspan = 1, sticky="nsew")
        
        self.right_frame = RightFrame(self)
        self.right_frame.grid(row=0, column=1, rowspan = 2, sticky="nsew")
        
        self.image_frame = imageFrame(self, right_frame_handle= self.right_frame)
        self.image_frame.grid(row=0, column=0, rowspan = 1, sticky="nsew")

        self.widget_list = [self.menu, self.navigation_frame, self.right_frame, self.image_frame]

        self.toggleControl()
        
        self.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.update_idletasks()
        self.mainloop()
    
    def organizeBackup(self):
        util.deleteOldFolders(self.base_path)
        util.createOrCleanFolder(self.backup_path)

    
    def onClosing(self):
        if (self.files_are_unsaved == True):
            message = msg.CTkMessagebox(title = 'Внимание', message = "Результаты анализа не были сохранены \n сохранить перед закрытием?",
                              icon = 'warning', option_1 = 'Да', option_2 = 'Нет', option_3 = "Отмена",)
            if (message.get() == 'Да'):
                self.menu.saveAll()
            elif(message.get() == 'Нет'):
                self.destroy()
        # if (self.image_frame cam!= 0):
        #     try:
        #         del self.image_frame.cam
        #     except: 
        #         print('Possibly there is still no cam object')
        else:
            self.destroy()

    def toggleControl(self):
        for widget in self.widget_list:
            widget.toggleControl()

    def setupGrid(self):
        self.grid_columnconfigure(0, weight=2)  
        self.grid_columnconfigure(1, weight=1)  
        self.grid_rowconfigure(0, weight=1)     
        self.grid_rowconfigure(1, weight = 0)
    
    def getImage(self):
        copy = self.camera_feed_image.copy()
        return copy

    def updateImage(self):
        self.current_image = self.getImage()





# if __name__ == "__main__":
#     # example_function()
    
#     app = App()
