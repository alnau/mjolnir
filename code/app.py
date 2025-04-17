import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
from PIL import Image, ImageTk,ImageDraw
import numpy as np
import threading
import time
from datetime import datetime


import customtkinter as ctk
import tkinter as tk
from  tkinter import filedialog, messagebox
from CTkMenuBar import *

import os
import logging
import traceback

# import error as e
import camera_feed_thorlabs as thor
from camera_feed_thorlabs import ThorCamera
import camera_feed_generic as gen
from camera_feed_generic import GenericCamera
import camera_feed_fake as fake
from camera_feed_fake import FakeCamera
import constants as const
import utility 
import image_processing as ip
from top_level import TopLevel
from bool_wrangler import boolWrangler



ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("dark-blue")  

class TitleMenu(CTkTitleMenu):
    def __init__(self, master):
        super().__init__(master)
        
        file_button = self.add_cascade("Файл")
        # reopen_camera_buttom = self.add_cascade("Изменить камеру", command = self.master.initUI)
        
        file_dropdown = CustomDropdownMenu(widget=file_button)
        extras_button = self.add_cascade("Дополнительно")
        self.exterminate_button = self.add_cascade("DoW")
        self.exterminate_button.configure(state = 'disabled')
        open_sub_menu = file_dropdown.add_submenu("Открыть")
        open_sub_menu.add_option(option="Файл", command = self.openFile)
        open_sub_menu.add_option(option="Папку", command = self.openFolder)

        recover_sub_menu  = file_dropdown.add_submenu("Восстановить сессию")

        for folder_name in self.master.backup_folders_names:
            recover_sub_menu.add_option(option = folder_name, command = lambda name = folder_name: self.recoverFromFolder(name))


        file_dropdown.add_separator()
        
        save_sub_menu = file_dropdown.add_option("Сохранить изображение", command = self.savePhoto)
        export_sub_menu = file_dropdown.add_submenu("Экспортировать")
        export_sub_menu.add_option(option = "Данные текущего изображения", command = self.exportFile)
        export_sub_menu.add_option(option = "Данные всех изображений", command = self.exportAll)
        
        extras_dropdown = CustomDropdownMenu(widget = extras_button)
        extras_dropdown.add_option("Изменить камеру", command = self.changeCamera)
        extras_dropdown.add_option("Начать новую серию измерений", command = self.resetStateAndData)
        extras_dropdown.add_option("Изменить отсечку фона", command = self.updateThreshold)

        geno_dropdown = CustomDropdownMenu(widget=self.exterminate_button)
        geno_dropdown.add_option(option = "NUKE EM, OPPIE!", command = self.restartInterface)
        geno_dropdown.add_option(option = "SHOOT YOUR OWN FOOT!", command = self.shotYourself)
        geno_dropdown.add_option(option = "TELL ME", command = self.dropInfo)
        geno_dropdown.add_option(option = 'BETTER CALL LESLIE GOVES', command = self.changeFlags)

        self.master.bind("<Control-Up>", self.onControl_UpPress)
        self.master.bind("<Control_L>", self.onControlPress)
        
        
        # self.bind("<ControlRelease>", self.onCtrlRelease)

    def changeFlags(self):
         
        flags_dict = {
            'data was reset': self.master.data_was_reset,
            'data is external': self.master.data_is_external,
            'navigation_frame: is active': self.master.navigation_frame.is_active,
            'right_frame: is active': self.master.right_frame.is_active,
            'photo is captured': self.master.photo_is_captured,
            'manual drawing': self.master.manual_drawing,
            'right_frame.tabview: needed active pos monitoring': self.master.right_frame.tabview.needed_active_pos_monitoring,
            'is pause': self.master.is_pause
        }
        bool_menu = boolWrangler(self.master, flags_dict)

    def changeCamera(self):
        self.resetStateAndData()
        self.master.initUI()

    def updateThreshold(self):
        val  = utility.getIniVal('cutoff_threshold')
        msg = 'Эта величина используется для определения уровня (0-255) для удаления подложки.'
        msg+= 'Все пиксели с интенсивности ниже данной величины будут считаться пикселями с нулевой интенсивностью.'
        msg = msg+'Текущее значение: ' + str(val)
        dialog = ctk.CTkInputDialog(text=msg, title="Введите уровень отсечки")
        new_val = int(dialog.get_input())  
        const.CUTOFF_THRESHOLD = new_val
        utility.updateIni('cutoff_threshold', new_val)
        msg = 'Текущий порог отсечения составляет:' + str(new_val)
        messagebox.showinfo(title = 'Данные обновлены', message = msg)
        

    def resetStateAndData(self):
        message =''
        if self.master.files_are_unsaved:
            message = 'У вас есть захваченные изображение или несохраненные результаты анализа\n'
        message += 'Если продолжить, все собранные данные будут сброшены. \nПродолжить?'

        answer = messagebox.askquestion(title='Внимание', message=message, )
        if answer == 'no':               
            return

        self.master.image_data_container = []
        
        self.master.image_index = 0

        # bool reset
        self.master.data_was_reset = True
        self.master.data_is_external = False
        self.master.navigation_frame.is_active = True
        self.master.photo_is_captured = False  
        self.master.right_frame.is_active = True   
        self.master.manual_drawing = False
           
        self.master.right_frame.tabview.needed_active_pos_monitoring = False

        self.master.is_pause = False      

    def dropInfo(self):
        print('\n\n--------------------------')
        print('Amount =', len(self.master.image_data_container))
        print('Curr index =', self.master.image_index)
        print("\nnames:")
        for id in self.master.image_data_container:
                print(id.image_name)

        print('\nFlags:')
        print('data_was_reset:',self.master.data_was_reset)
        print('data_is_external:',self.master.data_is_external) 
        print('navigation_frame.is_active:',self.master.navigation_frame.is_active)
        print('photo_is_captured:',self.master.photo_is_captured)
        print('right_frame.is_active:',self.master.right_frame.is_active)
        print('right_frame.tabview.needed_active_pos_monitoring:',self.master.right_frame.tabview.needed_active_pos_monitoring)
        print('app.manual_drawing:', self.master.manual_drawing)
        print('app.is_pause:',self.master.is_pause)

        utility.printIni()

        print('--------------------------\n\n')

    def savePhoto(self): 
        data = [("Изображения png", "*.png")]

        dir_path = filedialog.asksaveasfilename(filetypes=data, defaultextension=data)
        if (dir_path):
            self.master.camera_feed_image.save(dir_path)


    def restartInterface(self):
        self.master.is_pause = False
        try:
            self.master.image_frame.forgetCamera()
        except Exception as e:
            logging.error(e,stack_info=True, exc_info=True)
            print('Exception durint restartInterface:', traceback.format_exc())
        self.master.initUI()


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
            logging.error(e,stack_info=True, exc_info=True)
            print("Leg had been shot successfully:", traceback.format_exc())


    def recoverFromFolder(self, folder_name):
        print(folder_name)
        self.master.is_pause = True
        dir_path = utility.resourcePath(self.master.base_path + folder_name)
        print(dir_path)
        names = []
        pure_names = []
        self.master.image_data_container = []

        
        for image_name in os.listdir(dir_path):
            if (image_name.endswith('.tif')):
                names.append(image_name)
        for name in names:
            image = Image.open(os.path.join(dir_path, name)).convert('L')
            pure_name,_ = os.path.splitext(name)
            pure_name = utility.removeSuffix(pure_name, '.tif')
            pure_names.append(pure_name)
            self.master.image_data_container.append(ip.ImageData(image, pure_name))

        length = len(self.master.image_data_container)
        if (length == 0):
            self.master.right_frame.logMessage('Ошибка при импорте')
            logging.error('Err occured during recovery from folder. Image_data_container is empty')
        
        # TODO: возможно, если подменить на switchImage, решится баг с подгрузкой
        self.master.image_frame.loadImage(self.master.image_data_container[0].norm_image, pure_names[0])
        
        text = "Восстановлено " + str(len(self.master.image_data_container)) + " изображений. Вы можете продолжить работу"
        self.master.right_frame.logMessage(text)
        self.master.right_frame.tabview.set('Обработка')
        self.master.navigation_frame.next_button.configure(state = 'normal')
        self.master.navigation_frame.prev_button.configure(state = 'normal')
        self.master.data_is_external = True

    def toggleControl(self):
        pass

    def openFile(self):
        # TODO: надо сделать возможным импорт png и jpg файлов
        file_path = filedialog.askopenfilename(filetypes = [("tif file(*.tif)","*.tif")], defaultextension = [("tif file(*.tif)","*.tif")])
        if file_path:
            try:
                _, tail= os.path.split(file_path)
                name, _ = os.path.splitext(tail)
                image = Image.open(file_path)
                pure_name,_ = os.path.splitext(name)
                self.master.image_data_container.append(ip.ImageData(image, pure_name))
                self.master.data_is_external = True
            except Exception as e:
            # Логируем исключение
                logging.error(e,stack_info=True, exc_info=True)
                print("Error during image import;:", traceback.format_exc())

    def openFolder(self):
        # TODO: решил большую часть проблем с подгрузкой, но все еще при открытии загружает правильное изображение, потом переключает его на заглушку. При этом нажатие на кнопки навигации возвращает все на круги своя. Пройдись дебагером и не еби мозги
        self.master.is_pause = True
        self.master.right_frame.logMessage('Начат импорт файлов...')
        self.master.image_data_container = []
        self.master.image_index = 0
        
        dir_path = filedialog.askdirectory()
        self.master.right_frame.tabview.analyze_all_button.configure(state = 'normal')
        self.master.right_frame.tabview.analyze_current_button.configure(state = 'normal')
    
        if dir_path:          
            names = []
            for image_name in os.listdir(dir_path):
                if (image_name.endswith('.tif')):
                    names.append(image_name)
            for name in names:
                image = Image.open(os.path.join(dir_path, name)).convert('L')
                pure_name,_ = os.path.splitext(name)
                pure_name = utility.removeSuffix(pure_name, '.tif')
                self.master.image_data_container.append(ip.ImageData(image, pure_name))
            
            self.master.right_frame.tabview.set('Обработка')
            
            # self.master.image_frame.loadImage(self.master.image_data_container[0].norm_image, names[0])
            self.master.navigation_frame.switch()
            # self.master.right_frame.updateWindowAfterAnalysis()
            # self.master.image_frame.reset()
            
            text = "Импортировано " + str(len(self.master.image_data_container)) + " изображений. Вы можете приступить к их обработке"
            self.master.right_frame.logMessage(text)
            self.master.navigation_frame.next_button.configure(state = 'normal')
            self.master.navigation_frame.prev_button.configure(state = 'normal')

            self.master.data_is_external = True
        else:
            self.master.is_pause = False

    def exportFile(self, path = ''):
        index = self.master.image_index
        image_data = self.master.image_data_container[index]
        image_data.plotBepis(path)
        
        self.master.right_frame.logMessage("Данные", image_data.image_name, "сохранены в папке")
                        
    def exportAll(self, path =''):
        dir_path = filedialog.askdirectory(title='Выберете папку для сохранения файлов')
        saving_thread = threading.Thread(target=self.exportAllWorker, args=(dir_path,))
        saving_thread.daemon = True 
        saving_thread.start()


        
    def exportAllWorker(self, path):
        new_names = []
        r_ref = 0

        self.master.setProgressBarActive()
        
        raw_dir = "Raw"
        raw_path = os.path.join(path, raw_dir)
        os.makedirs(raw_path)

        if (self.master.continue_unstructured):
            width_data = []
            for image_data in self.master.image_data_container:
                
                self.master.update_idletasks()
                image_data.plotBepis(path)
                name = image_data.image_name
                raw_image = image_data.initial_image

                image_path = os.path.join(raw_path, name) + ".tif"
                raw_image.save(image_path)
                
                if (name !='control'):
                    width_data.append(round(2*image_data.radius_mm, 2))
                    new_names.append(name)
                elif (image_data.image_name == 'control'):
                    r_ref = round(2*image_data.radius_mm,2)
            print("------------------")
            utility.printUnstructuredReportToXLSX(new_names, width_data, r_ref, path)
        else:
            width_data_d = []
            width_data_o = []
            for image_data in self.master.image_data_container:
                
                self.master.update_idletasks()
                image_data.plotBepis(path)
                name = image_data.image_name
                raw_image = image_data.initial_image

                image_path = os.path.join(raw_path, name) + ".tif"
                raw_image.save(image_path)
                if (name != 'control'):
                    number, test_for_d_o = image_data.image_name.rsplit("_",1)
                    if (test_for_d_o == "d"):
                        width_data_d.append(round(2*image_data.radius_mm, 2))
                        if number not in new_names:
                            new_names.append(number)
                    elif (test_for_d_o == "o"):
                        width_data_o.append(round(2*image_data.radius_mm,2))
                        if number not in new_names:
                            new_names.append(number)
                elif (image_data.image_name == 'control'):
                    r_ref = round(2*image_data.radius_mm,2)
            print("------------------")
            utility.printReportToXLSX(new_names, width_data_d, width_data_o, r_ref, path)  

        self.master.setProgressBarInactive()
        self.master.right_frame.logMessage('Данные измерений сохранены')
        self.master.files_are_unsaved = False



class NavigationFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.is_active = True #bool

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", pady=const.DEFAULT_PADY, padx = const.DEFAULT_PADX, side = 'top')
        button_frame.grid_columnconfigure(0, weight=3)
        button_frame.grid_columnconfigure(1, weight=3)
        
        self.prev_button = ctk.CTkButton(button_frame, text="<", 
                                        command = lambda: self.switch(btn = 'back'))
        self.prev_button.grid(row = 0, column = 0, sticky = 'e', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY)


        self.next_button = ctk.CTkButton(button_frame, text=">", 
                                        command = lambda: self.switch(btn = "fwd"))
        self.next_button.grid(row = 0, column = 1, sticky = 'w', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY)

        self.master.bind('<Left>', lambda event: self.switch(btn = 'back'))
        self.master.bind('<Right>', lambda event: self.switch(btn = 'fwd'))

    # посылает сигнал о переключении картинок
    def switch(self, event = None, btn = ''):
        if self.next_button.cget('state') == 'disabled':
            return
        
        if (btn == 'fwd'):
            self.master.image_index = min(self.master.image_index+1, len(self.master.image_data_container) - 1)
        elif btn == 'back':
            self.master.image_index = max(0, self.master.image_index - 1)
        else:
            pass
        name = ''
        if (len(self.master.image_data_container)!= 0):
            
            name = self.master.image_data_container[self.master.image_index].image_name
        was_analyzed = False
        try:
            was_analyzed = self.master.image_data_container[self.master.image_index].image_has_been_analyzed
        except Exception as e:
            print('Can not get access to self.master.image_data_container[self.master.image_index].image_has_been_analyzed', traceback.format_exc())
            logging.error(e,stack_info=True, exc_info=True)
            
        self.master.right_frame.entry.configure(placeholder_text = name)
        self.master.right_frame.curr_name_str_val.set(name)
        
        # TODO: возможно, можно не передавать image_index в эти функции
        self.master.right_frame.updatePlotAfterAnalysis(self.master.image_index, was_analyzed)
        self.master.right_frame.updatePrintedDataAfterAnalysis(self.master.image_index)
        # TODO: убрал 10.02.25 за ненадобностью. Возможно, ошибся
        # self.master.image_frame.loadImage(self.master.image_data_container[self.master.image_index].norm_image, name = self.master.image_data_container[self.master.image_index].image_name)
        self.master.image_frame.switchImage(self.master.image_index)
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





class ImageFrame(ctk.CTkFrame):
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

        self.start_dialog = ctk.CTkFrame(self)
        self.start_dialog.pack(fill="both", padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY, expand=True)

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
        
        self.image_canvas.bind("<ButtonPress-1>", self.draw )
        self.image_canvas.bind("<B1-Motion>", self.draw )
        self.image_canvas.bind("<ButtonRelease-1>", self.draw )
        self.image_canvas.bind("<ButtonRelease-1>", self.draw )

    def getCameraList(self):
        tmp_camera_list = []
        if (fake.isCameraConnected()):
            tmp_camera_list.append("Пустышка")
        if (thor.isCameraConnected()):
            tmp_camera_list.append("ThorCam")
        for i in range(10):
            if (gen.isCameraConnected(i)):
                text = 'USB - камера ' + str(i) 
                tmp_camera_list.append(text)
        tmp_camera_list.append("Обновить список")

        return tmp_camera_list
    
    def chooseCamera(self, choise):
        if (choise == 'Пустышка'):
            self.cam = FakeCamera()
            self.start_button.configure(state = 'normal')
        if (choise == 'ThorCam'):
            self.cam = ThorCamera()
            self.start_button.configure(state = 'normal')
        elif(choise[:-2] == 'USB - камера'):
            index = int(choise[-1])
            self.cam = GenericCamera(index)
            self.start_button.configure(state = 'normal')
        elif(choise == 'Обновить список'):
            self.camera_list = self.getCameraList()
            self.camera_selection.configure(values = self.camera_list)

    def forgetCamera(self):
        try:
            # self.cam.__delete__()
            self.cam.releaseCamera()
            self.cam = FakeCamera()
        except Exception as e:
            logging.error(e,stack_info=True, exc_info=True)
            print("failed to delete camera", traceback.format_exc())
        
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
        self.master.right_frame.tabview.sliderEvent(const.MAX_EXPOSURE_MS/2)
        while True:
            # запросим последнее изображение с камеры и загрузим его в app.camera_feed_image
            self.cam.cameraFeed(master_app=self) 
            self.master.right_frame.tabview.checkForOverexposure()
            if (self.master.is_pause or self.master.right_frame.tabview.needed_active_pos_monitoring):
                # Если изображение захвачено (is_pause == True) или мы измеряем клиновидность, отключить автоообновление
                # картинки с камеры
                pass
            else:
                # подменим app.current_image TODO: раньше было до if
                self.master.updateImage()
                self.updateCanvas(self.master.current_image)
            self.master.update_idletasks()
            time.sleep(0.05)

    # вызываетя после выбора камеры. Убивает диалоговое окно с выбором и переключает на живую 
    # трансляцию
    def activateCamera(self):
        self.start_dialog.pack_forget()
        self.image_canvas.pack(fill="both", padx = (5,0), pady = const.DEFAULT_PADY, expand=True)
        self.bind("<Configure>", self.resizeImage)
        self.resizeImage(None)
        self.master.toggleControl()
        # self.resizeImage(None)
        self.master.right_frame.tabview.slider.set(self.cam.getExposureFrac()) 
        self.master.right_frame.tabview.slider2.set(self.cam.getExposureFrac()) 
        self.master.right_frame.tabview.slider3.set(self.cam.getExposureFrac()) 
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

    def draw(self, event):
        if (self.master.right_frame.tabview.get() == 'Обработка' or  self.master.data_is_external == True):
            self.drawLines(event)
        elif (self.master.right_frame.tabview.get() == 'Ручной режим' and self.master.manual_drawing):
            self.drawCircles(event)

    def drawCircles(self,event):
        tabview_handle = self.master.right_frame.tabview 

        if (event.type == '4'):
            # нажали
            # логика отделения 
            if (tabview_handle.first_center_coords == None):
                tabview_handle.first_center_coords = (event.x, event.y)
                tabview_handle.p0 = (tabview_handle.first_center_coords[0]/self.master.crop_factor_x, tabview_handle.first_center_coords[1]/self.master.crop_factor_y)
                tabview_handle.second_center_coords = None
                tabview_handle.p1 = (0,0)

            else:
                tabview_handle.second_center_coords = (event.x, event.y)
                tabview_handle.p1 = (tabview_handle.second_center_coords[0]/self.master.crop_factor_x, tabview_handle.second_center_coords[1]/self.master.crop_factor_y)
            # self.clearPhoto()   # Тут тоже надо подумать, требется накладывать первый и второй круги
        elif (event.type == '6'):
            # тащим
            coords_image_space = (event.x, event.y)
            if (tabview_handle.second_center_coords == None):
                tabview_handle.first_radius_image_space = utility.getRadius(tabview_handle.first_center_coords, coords_image_space) 
            else:
                tabview_handle.second_radius_image_space = utility.getRadius(tabview_handle.second_center_coords, coords_image_space)

            # updated_image = self.updateCircleOnPhoto(tabview_handle.first_center_coords, tabview_handle.first_radius_image_space)
            # photo = ImageTk.PhotoImage(updated_image)
            # self.image_canvas.config(width=updated_image.width, height=updated_image.height)
            # self.image_canvas.create_image(0,0,image=photo,anchor = 'nw')
            # self.image_canvas.image = photo
        elif (event.type == '5'):
            # отпустили
            if (tabview_handle.second_center_coords!=None and tabview_handle.first_center_coords!=None ):
                # посчитали и вывели угол
                tabview_handle.manualySetCoords()
                



    def drawLines(self, event):    
        index = self.master.image_index
        length = len(self.master.image_data_container)
        if (event.type == '4'):
            # нажали
            # тут какая-то полная грязь с логикой. Я уже слишком пьян чтобы разобраться в этом дерьме
            # фактически ифы ниже только для того, чтобы нормально отрабатывала логика сброса галки о том, 
            # что оптимизация не нужна. Уверен, на трезвую голову ты справишься куда лучше
            # 
            # При этом, все работает
            # elif(length != 0 and index < length):
            #     # TODO: Есть сценарии, при которых индекс может вести за пределы массива. Не знаю как решать эту проблему
            #     # print('index =', index)
            #     self.master.image_data_container[index].line_was_built = False
            #     self.master.image_data_container[index].optimisation_needed = True
            self.master.right_frame.clearPlot()
            tabview_handle = self.master.right_frame.tabview 
            # tabview_handle.check_var.set('on')
            self.tmp_coords = (0,0)
            self.start_coords = (event.x, event.y)
            tabview_handle.analyze_all_button.configure(state = 'normal')
            tabview_handle.analyze_current_button.configure(state = 'normal')
            self.clearPhoto()
            
        elif (event.type == '5'):
            # Отпустили
            self.end_coords = (event.x, event.y)
            self.tmp_coords = self.end_coords
            self.p0_real_coords = (int(self.start_coords[0]*self.master.current_image.width/self.image_resized.width), int(self.start_coords[1]*self.master.current_image.height/self.image_resized.height))
            self.p1_real_coords = (int(self.end_coords[0]*self.master.current_image.width/self.image_resized.width), int(self.end_coords[1]*self.master.current_image.height/self.image_resized.height))
            self.right_frame_handle.updatePlot(self.p0_real_coords, self.p1_real_coords)
            self.master.image_data_container[index].line_was_built = True
            # print(index)

        elif (event.type == '6'):
            # Тащим
            self.tmp_coords = (event.x, event.y)
        if (self.tmp_coords != (0,0)):
            updated_image = self.updateLineOnPhoto()
            
            photo = ImageTk.PhotoImage(updated_image)

            self.image_canvas.config(width=updated_image.width, height=updated_image.height)
            self.image_canvas.create_image(0,0,image=photo,anchor = 'nw')
            self.image_canvas.image = photo
        # else:
        #     self.master.right_frame.logMessage("Необходимо сначала захватить изображение")

    
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
        
        tabview_handle = self.master.right_frame.tabview

        photo = None

        if (self.master.manual_drawing and tabview_handle.first_center_coords != None):
            updated_image = self.updateCircleOnPhoto(tabview_handle.first_center_coords, tabview_handle.first_radius_image_space)
            if (tabview_handle.second_center_coords != None):
                updated_image = self.updateCircleOnPhoto(tabview_handle.second_center_coords, tabview_handle.second_radius_image_space, updated_image)
        else:
            updated_image = self.image_resized
 
        
        photo = ImageTk.PhotoImage(updated_image)
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

        self.draw.ellipse(utility.getCircleBound(self.start_coords, const.CIRCLE_RADIUS), fill = const.LINE_COLOR, width = const.LINE_WIDTH)
        self.draw.ellipse(utility.getCircleBound(self.tmp_coords, const.CIRCLE_RADIUS), fill = const.LINE_COLOR, width = const.LINE_WIDTH)
        self.draw.line([self.start_coords, self.tmp_coords], fill = const.LINE_COLOR, width = const.LINE_WIDTH)
        if (self.master.right_frame.tabview.needed_active_pos_monitoring):
            point = self.master.right_frame.tabview.p0
            self.draw.line(self.getCrossLineCoord(point,True), fill = const.LINE_COLOR, width = const.LINE_WIDTH)
            self.draw.line(self.getCrossLineCoord(point,False), fill = const.LINE_COLOR, width = const.LINE_WIDTH)
        return tmp_image
    
    def updateCircleOnPhoto(self,start, radius, image = None):
        if (image != None):
            tmp_image = image.copy()
        else:
            tmp_image = self.image_resized.copy()
        self.draw = ImageDraw.Draw(tmp_image)
        self.draw.ellipse(utility.getCircleBound(start, radius), fill = None, width = const.LINE_WIDTH, outline = const.LINE_COLOR)
        
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
        
        index = min(self.master.image_index, len(self.master.image_data_container)-1)
        if (index < 0):
            index = 0
        self.master.right_frame.entry.configure(placeholder_text = name)
        self.master.right_frame.curr_name_str_val.set(name)
        text = str(index + 1) 
        L = ctk.CTkLabel(self.image_canvas, text = text, fg_color = 'transparent', width = 20, text_color = 'black')
        L.place(x = 10,y = 10, anchor = 'nw')

    def switchImage(self, index):
        """ Оболочка для loadImage, преобразающая данныe imageData в изображение, в зависимости от того, было ли оно обработано"""
        idata = self.master.image_data_container[index]
        name = ''
        if (idata != 'None'):
            name = idata.image_name
        else:
            print('image data is empty. Returning')
            return
        if (idata.image_has_been_analyzed):
            self.loadImage(idata.modified_image, name)
        else:
            self.loadImage(idata.norm_image, name)

    def resizeImage(self, event):
        # TODO разберись уже с этой функцией, это уже непрофессионально
        
        self.master.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()

        # загрузим изображение, отмасштабируем и конвертируем его
        image = self.master.current_image
        self.image_resized = image.resize((width, height))
        self.photo = ImageTk.PhotoImage(self.image_resized)
        self.master.update_idletasks()
        # обновим холст 
        self.image_canvas.config(width=self.image_resized.width, height=self.image_resized.height)
        self.image_canvas.create_image(0,0,image=self.photo,anchor = 'nw')
        self.image_canvas.image = self.photo
        
        # ... и данные по кропу. отношение размера окна к изображению
        self.master.crop_factor_x = width/self.master.current_image.width
        self.master.crop_factor_y = height/self.master.current_image.height

        
        
        self.master.update_idletasks()

class RightFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.is_active = True   #bool

        plot_width = 4.5
        plot_height = 2.7

        

        self.tmp_name = ''

        self.fig, self.ax = plt.subplots(figsize=(plot_width, plot_height)) 
        plt.tight_layout(pad=0) 
        self.ax.set_aspect('auto', adjustable='box')

        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().pack(fill="x", padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY, side = "top")

        entry_frame = ctk.CTkFrame(self, )
        entry_frame.pack(fill="x", pady=const.DEFAULT_PADY/2, padx = const.DEFAULT_PADX, side = 'top')
        
        # Это будет самое безбожное, что ты делал с этим проектом
        self.curr_name_str_val = ctk.StringVar()
        self.curr_name_str_val.trace_add('write', self.updateName)
        self.entry = ctk.CTkEntry(entry_frame, textvariable=self.curr_name_str_val)
        self.entry.pack(fill="x", side = 'left', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY, expand = True)
        self.entry.focus()
        
        self.capture_button = ctk.CTkButton(entry_frame, text = 'Захватить', command= self.captureImage)
        self.capture_button.pack(side = 'left', pady = const.DEFAULT_PADY, padx = const.DEFAULT_PADX)
        self.master.bind('<Return>', self.handleEnter)
    
        thin_frame = ctk.CTkFrame(self, height=2, bg_color="gray")
        thin_frame.pack(fill="x", padx =10, pady=const.DEFAULT_PADY/2,)

        self.tabview = Tab(master = self, main=master)
        self.tabview.pack(side = 'top', fill = 'both', pady = (0,const.DEFAULT_PADY), padx = const.DEFAULT_PADX) 
        

        frame_frame = ctk.CTkFrame(self, height = master.navigation_frame.winfo_height())
        frame_frame.pack(fill="x", padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY, side = 'bottom')

        self.status = ctk.CTkLabel(frame_frame, text = '', )   
        self.status.pack( fill = 'both', pady = const.DEFAULT_PADY, padx = const.DEFAULT_PADX)

    def updateName(self,var,index,mode):
        try:
            # TODO: Вылезает ошибка, но, вроде, обрабатывается исключением
            if (len(self.master.image_data_container)==0):
                name = self.curr_name_str_val.get()
                self.entry.configure(placeholder_text = name)
                self.tmp_name = name
                return
            
            # TODO на текущий момент исправления в имени файла между захватом изображения и переходом к следующему кадру невозможны 
            _index = self.master.image_index
            name = self.curr_name_str_val.get()
            if self.tabview.get() == 'Захват':
                # if self.master.photo_is_captured:
                    # При этом оставим возможность редактуры после захвата
                # self.master.image_data.image_name = name 
                # Возможно, исправит ошибку. В режиме захвата мы все равно не можем 
                # переключать кадры, так что вовлекать индексы и image_data_container нет никакого смысла.
                pass
            else:
                # На самом деле, проявляется только в режиме обработки изображений. Но пока это 
                # взаимозаменяемые вещи
                self.master.image_data_container[_index].image_name = name
            self.entry.configure(placeholder_text = name)
            self.tmp_name = name
        except Exception as e:
            logging.error(e,stack_info=True, exc_info=True)
            print('exception in updateName;', traceback.format_exc())
            _index = self.master.image_index
            name = self.curr_name_str_val.get()
            self.entry.configure(placeholder_text = name)
            self.tmp_name = name

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
        self.tabview.continue_button.configure(state = 'normal')
        self.master.image_frame.image_canvas.configure(highlightbackground="red")
        self.master.photo_is_captured = True
        self.master.image_frame.loadImage(self.master.current_image, self.tmp_name)

        self.logMessage('Фото захвачено')

    def unlockCamera(self):
        self.master.is_pause = False
        self.capture_button.configure(text = 'Захватить')
        self.tabview.continue_button.configure(state = 'disabled')
        self.master.image_frame.image_canvas.configure(highlightbackground="black")
        self.master.photo_is_captured = False
        self.master.image_frame.clearPhoto()

    def nextImage(self):
        self.master.image_index += 1
        if len(self.entry.get()) != 0:
            
            # self.tabview.check_var.set('off')
            self.entry.focus()
            self.master.image_data.p0_new = self.master.image_frame.p0_real_coords
            self.master.image_data.p1_new = self.master.image_frame.p1_real_coords

            self.master.image_data.p0_im_space = self.master.image_frame.start_coords
            self.master.image_data.p1_im_space = self.master.image_frame.end_coords

            self.master.image_data_container.append(self.master.image_data)
            self.master.files_are_unsaved = True


            need_to_check_for_duplicate = True
            number = ''
            pure_name = ''
            file_path = ''
            counter = 0
            # Логика проверки на существование дубликата. Добавляет в конце
            # названия цифры 1, 2, 3... пока не найдет незанятого имени
            while(need_to_check_for_duplicate):

                pure_name = self.entry.get()
                file_name = self.entry.get() + number + '.tif'
                file_path = os.path.join(self.master.backup_path, file_name) 
                if (os.path.exists(file_path)):
                    counter+=1
                    number  = '(' + str(counter) + ')'
                else:
                    need_to_check_for_duplicate  = False

            print('Бэкап создан. Путь:', file_path)
            msg = 'Данные ' + pure_name + ' записаны в буфер'
            self.logMessage(msg)
            self.entry.delete(0, 'end')
            
            self.master.image_data.initial_image.save(file_path)
            
            # self.image_data = None

            self.unlockCamera()

            self.master.image_frame.reset()

            # Разблокировать чекбоксы, заблокированные после обработки, если пользователь решил добавить данные 
            self.tabview.draw_line_checkbox.configure(state = 'normal')
            self.tabview.draw_circle_checkbox.configure(state = 'normal')
        else:
            self.logMessage('Введите название файла')

    
    def handleEnter(self, event):
        
        if (self.tabview.get() == 'Захват'):
            if (self.master.photo_is_captured):
                self.nextImage()
            else:
                self.captureImage()
        if (self.tabview.get() == 'Клиновидность'):
            self.tabview.setFirstPosition()

    def captureImage(self):
        # отработка захвата или сброса текущего изображения
        self.master.data_is_external = False
        if (self.master.photo_is_captured):
            # self.master.navigation_frame.image_index = max(0,self.master.navigation_frame.image_index-1)
            # переход к живой камере
            self.unlockCamera()
            self.logMessage('Фото сброшено')
            # чисто на всякий пожарный снимем все возможные триггеры на пропуск оптимизации 
            self.master.image_frame.start_coords = (0,0)
            self.master.image_frame.end_coords = (0,0)
            # self.tabview.check_var.set('off')
        elif(len(self.tmp_name)!=0) :
            # self.master.navigation_frame.image_index += 1
            # Показать картинку, сохранить в буффер
            self.lockCamera()
            self.master.image_data = ip.ImageData(self.master.current_image, self.entry.get())
        else:
            self.logMessage('Введите имя файла')

        
    def clearPlot(self):
        self.ax.clear()
        self.plot_canvas.draw()

    def updatePlot(self, p0, p1): 
        
        self.master.image_data.p0_initial = p0
        self.master.image_data.p1_initial = p1
        coords, brightness = utility.getBrightness(p0, p1,self.master.current_image)
        self.ax.clear()
        self.ax.plot(coords, brightness)
        # Каждый мм
        self.ax.xaxis.set_major_locator(MultipleLocator(1))
        # Каждые 0.2 мм (1/5 = 0.2)
        self.ax.xaxis.set_minor_locator(AutoMinorLocator(5))

        if (max(brightness) < 10):
            # каждые 50 ед
            self.ax.yaxis.set_major_locator(MultipleLocator(0.2))
            # Каждые 10 ед (0.2/2 = 0.1)
            self.ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        else:
            # каждые 50 ед
            self.ax.yaxis.set_major_locator(MultipleLocator(50))
            # Каждые 10 ед (50/5 = 10)
            self.ax.yaxis.set_minor_locator(AutoMinorLocator(5))
        
        self.ax.grid(which = 'both')
        self.ax.grid(which = 'major', linestyle = '--')
        self.ax.grid(which = 'minor', linestyle =':')
        self.plot_canvas.draw()

    # def updateWidowOnSwitch(self):
    #     self.after(100, self.tabview.configure(state = 'normal'))
    #     index = self.master.navigation_frame.image_index
    #     self.updatePlotAfterAnalysis(index)
    #     self.updatePrintedDataAfterAnalysis(index)
    #     self.master.image_frame.switchImage(index)

    def updateWindowAfterAnalysis(self):
        # try:
    
        self.after(100, self.tabview.configure(state = 'normal'))
        index = min(self.master.image_index, len(self.master.image_data_container) - 1)
        self.updatePlotAfterAnalysis(index)
        self.updatePrintedDataAfterAnalysis(index)
        self.master.image_frame.switchImage(index)
        self.tabview.analyze_all_button.configure(state = 'disabled')
        self.tabview.analyze_current_button.configure(state = 'disabled')
        # except:
        #     print('You know, I''m just hanging around, anyways, checkout updateWidndowAfterAnalysis()')

    def updatePlotAfterAnalysis(self, index, was_analyzed = True):
        idata = self.master.image_data_container[index]

        self.ax.clear()
        if was_analyzed:
            self.ax.plot(idata.coord, idata.normalized_brightness_values)
            # Каждый мм
            self.ax.xaxis.set_major_locator(MultipleLocator(1))
            # каждые 50 ед
            self.ax.yaxis.set_major_locator(MultipleLocator(0.2))

            # Каждые 0.2 мм (1/5 = 0.2)
            self.ax.xaxis.set_minor_locator(AutoMinorLocator(5))
            # Каждые 10 ед (0.2/2 = 0.1)
            self.ax.yaxis.set_minor_locator(AutoMinorLocator(2))
            self.ax.grid(which = 'both')
            self.ax.grid(which = 'major', linestyle = '--')
            self.ax.grid(which = 'minor', linestyle =':')
        self.plot_canvas.draw()

    def updatePrintedDataAfterAnalysis(self, index):
        self.tabview.displayReport()


class Tab(ctk.CTkTabview):
    def __init__(self, master, main, **kwargs):
        super().__init__(master, **kwargs)

        self.main = main

        self.angle_thread = None

        self.configure(command = self.tabHandler)

        self.pack(fill="x", expand = True)

        self.p0 = (100,100)
        self.p1 = (0,0)

        self.angle_sec = 0

        self.needed_active_pos_monitoring = False   #bool

        #################   Захват   #########################

        capture_tab = self.add("Захват")  
          
        slider_frame = ctk.CTkFrame(capture_tab, fg_color='transparent')
        slider_frame.pack(fill = 'x', side = 'top')

        slider_label = ctk.CTkLabel(slider_frame, text='Экспозиция    ')
        slider_label.pack(side = 'left')
        self.slider = ctk.CTkSlider(slider_frame, from_ = 0,to = const.MAX_EXPOSURE_MS, command = self.sliderEvent)
        self.slider.pack(fill = 'x', side = 'left', expand = True) 

        self.max_exposure_label = ctk.CTkLabel(slider_frame, text = '')
        self.max_exposure_label.pack(side = 'left')

        option_frame = ctk.CTkFrame(capture_tab, fg_color='transparent')
        option_frame.pack(side = 'top', fill = 'x', pady = (10,0))
        
    
        # self.check_var = ctk.StringVar(value="off")
        # self.select_optimisation_button = ctk.CTkCheckBox(option_frame, onvalue= 'on', offvalue = 'off', variable= self.check_var, text = 'Использовать пользовательскую линию для анализа')
        # self.select_optimisation_button.grid(sticky = 'nw')

        # TODO: command = self.master.nextImage - это что-то совсем безбожное
        self.continue_button = ctk.CTkButton(master = capture_tab, command = self.master.nextImage, text = 'Продолжить', state = 'disabled')
        self.continue_button.pack(side = 'bottom', fill = 'x')

        #################     Обработка   #########################
        analyze_tab = self.add("Обработка")

        button_frame = ctk.CTkFrame(analyze_tab, fg_color='transparent')
        button_frame.pack(fill = 'x', anchor = 'n')
        button_frame.grid_columnconfigure((0,1), weight = 1)
        self.analyze_all_button = ctk.CTkButton(button_frame, text = 'Обработать все', command= lambda: self.analyzeAll(data_container = self.main.image_data_container))
        self.analyze_all_button.grid(row = 0, column = 1, sticky = 'ew', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY)
        self.analyze_current_button = ctk.CTkButton(button_frame, text = 'Обработать отдельные кадры', command=self.selectFramesToAnalyze)
        self.analyze_current_button.grid(row = 0, column = 0, sticky = 'ew', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY)
        
        
        analysis_frame = ctk.CTkScrollableFrame(analyze_tab)
        analysis_frame.pack(fill = 'both',anchor = 'n', expand = True)
        
        self.draw_line_var = ctk.IntVar(value=0)
        self.draw_line_checkbox = ctk.CTkCheckBox(analysis_frame, onvalue= 1, offvalue = 0, variable= self.draw_line_var, text = 'Вывести линию главной оси')
        self.draw_line_checkbox.pack(anchor = 'nw', pady = const.DEFAULT_PADY)
        self.draw_line_var.trace_add('write', self.changeNeedToDrawLine)

        self.draw_circle_var = ctk.IntVar(value=1)
        self.draw_circle_checkbox = ctk.CTkCheckBox(analysis_frame, onvalue= 1, offvalue = 0, variable= self.draw_circle_var, text = 'Вывести окружность 86.5% энергии')
        self.draw_circle_checkbox.pack(anchor = 'nw', pady = const.DEFAULT_PADY)
        self.draw_circle_var.trace_add('write', self.changeNeedToDrawCircle)
        

        self.report_textbox = ctk.CTkTextbox(analysis_frame)
        self.report_textbox.insert('0.0', 'Данные не обработаны')
        self.report_textbox.configure(state = 'disabled')
        self.report_textbox.pack(fill = 'x', side = 'top')
        # self.report_textbox.grid(row = 0, column = 0, sticky = 'new', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY)

        #################   Клиновидность   #########################
        parallelism_tab = self.add("Клиновидность")

        self.slider_frame2 = ctk.CTkFrame(parallelism_tab, fg_color='transparent')
        self.slider_frame2.pack(fill = 'x', side = 'top')


        self.slider_label2 = ctk.CTkLabel(self.slider_frame2, text='Экспозиция    ')
        self.slider_label2.pack(side = 'left')
        self.slider2 = ctk.CTkSlider(self.slider_frame2, from_ = 0,to = const.MAX_EXPOSURE_MS, command = self.sliderEvent)
        self.slider2.pack(fill = 'x', side = 'left', expand = True) 

        self.max_exposure_label2 = ctk.CTkLabel(self.slider_frame2, text = '')
        self.max_exposure_label2.pack(side = 'left')
        
        base_entry_frame = ctk.CTkFrame(parallelism_tab, )
        base_entry_frame.pack(fill="x", pady=(10, 5), side = 'top')
        
        base_label = ctk.CTkLabel(base_entry_frame, text = 'База (см)')
        base_label.pack(side = 'left', pady = const.DEFAULT_PADY, padx = const.DEFAULT_PADX)
        
        self.base_var = ctk.StringVar(self.main,value = str(const.DEFAULT_BASE_CM))
        self.base_entry = ctk.CTkEntry(base_entry_frame, textvariable=self.base_var)
        self.base_entry.pack(fill="x", side = 'left', padx = const.DEFAULT_PADX, pady = const.DEFAULT_PADY, expand = True)
        self.base_var.trace_add('write', self.updateBase)

        # self.base_entry.insert(0, str(const.DEFAULT_BASE_CM))

        first_button = ctk.CTkButton(parallelism_tab, text = 'Записать первую точку', command=self.setFirstPosition)
        first_button.pack(fill = 'x', side = 'top')
    
        res = self.getParallelismReport()
        self.resultsLabel = ctk.CTkLabel(parallelism_tab, text =res , anchor= 'n')
        self.resultsLabel.pack(fill = 'x', expand = True, side = 'top', pady = 2)
        self.resultsLabel.cget("font").configure(size=45)

        #################   Ручной режим   #########################
        manual_tab = self.add('Ручной режим')

        self.first_center_coords = None
        self.first_radius_image_space = 0

        self.second_center_coords = None
        self.second_radius_image_space = 0

        self.slider_frame3 = ctk.CTkFrame(manual_tab, fg_color='transparent')
        self.slider_frame3.pack(fill = 'x', side = 'top')
        
        self.slider_label3 = ctk.CTkLabel(self.slider_frame3, text='Экспозиция    ')
        self.slider_label3.pack(side = 'left')
        self.slider3 = ctk.CTkSlider(self.slider_frame3, from_ = 0,to = const.MAX_EXPOSURE_MS, command = self.sliderEvent)
        self.slider3.pack(fill = 'x', side = 'left', expand = True) 

        self.max_exposure_label3 = ctk.CTkLabel(self.slider_frame3, text = '')
        self.max_exposure_label3.pack(side = 'left')

        self.discard_manual_button = ctk.CTkButton(manual_tab, text = 'Сбросить результаты', command = self.discardManual)
        self.discard_manual_button.pack(fill = 'x', side = 'top', pady = 2)        
        self.manual_resultsLabel = ctk.CTkLabel(manual_tab, text = 'NA', anchor= 'n')
        self.manual_resultsLabel.pack(fill = 'x', expand = True, side = 'top', pady = 2)
        self.manual_resultsLabel.cget("font").configure(size=45)


        self.tabHandler()

    def discardManual(self):
        self.first_center_coords = None
        self.second_center_coords = None
        self.discard_manual_button.configure(text = 'NA')

    def changeNeedToDrawLine(self,var,index,mode): 
        # self.draw_line_var
        
        for i in range(len(self.main.image_data_container)):
            self.main.image_data_container[i].need_to_draw_line = self.draw_line_var.get() 
            # print(self.main.image_data_container[i].need_to_draw_line)
        # print('Need to draw line:', self.main.image_data_container[0].need_to_draw_line)

    def changeNeedToDrawCircle(self,var,index,mode): 
        # self.draw_line_var
        if self.main.image_data_container[0].radius_was_calculated:
            # TODO: в случае, когда данные уже были проанализированы и произошел переворот этого флага, необходимо подменить данные только для этого изображения
            # возможно имеет смысл после анализа все-таки связывать эти флаги 
            # с каждым индивидуальным изображением. Плевать, пока заморожу чекбоксы после обработки  
            pass
        for i in range(len(self.main.image_data_container)):
            self.main.image_data_container[i].need_to_draw_circle = self.draw_circle_var.get()
        # print('Need to draw circle:', self.main.image_data_container[0].need_to_draw_circle)
    

    def updateBase(self,var,index,mode):
        new_base = self.base_var.get()
        if (new_base!=''):
            const.DEFAULT_BASE_CM = int(new_base)
            utility.updateIni('default_base_cm', new_base)


    def displayReport(self):
        if (len(self.main.image_data_container) == 0):
            return
        data_was_analyzed = False
        index = 0
        tmp_image_data = 0
        try:
            last_index = len(self.main.image_data_container) - 1
            index = min(self.main.image_index, last_index)
            tmp_image_data = self.main.image_data_container[index]
            data_was_analyzed = tmp_image_data.radius_was_calculated
        except Exception as e:
            
            logging.error(e,stack_info=True, exc_info=True)
            print("well, no luck on report printout side. Possibly, there is nothing inside image_data_container;", traceback.format_exc())

            if (tmp_image_data == 0):
                print('Yeah, just checked, seems like it. Try to find workaround, godspeed')
                logging.error('Yeah, just checked, seems like it. Try to find workaround, godspeed')
        
        self.report_textbox.configure(state = 'normal')
        self.report_textbox.delete('0.0', 'end')
        if (data_was_analyzed and self.get() == 'Обработка'):
            report_text = tmp_image_data.report
            self.report_textbox.insert('0.0', report_text)
        else:
            self.report_textbox.insert('0.0', 'Данные не обработаны')
        self.report_textbox.configure(state = 'disabled')
     


    def tabHandler(self):
        if (self.get() == 'Захват'):
            # self.lockNameFromChanges()
            self.main.is_pause = False
            self.needed_active_pos_monitoring = False
            if (self.angle_thread!= None):
                self.angle_thread.join()
            self.main.navigation_frame.next_button.configure(state = 'disabled')
            self.main.navigation_frame.prev_button.configure(state = 'disabled')
            self.master.capture_button.configure(state = 'normal')
            self.p1 = (0,0)
            # Обеспечим то, что счетчик указывает на последний эл-т в image_data_container 
            self.main.image_index = max(0, len(self.main.image_data_container) - 1)
            self.main.manual_drawing = False
            self.first_center_coords = None
            self.second_center_coords = None
        elif (self.get() == 'Обработка'):
            # self.lockNameFromChanges()
            # TODO: все еще грязый трюк, но время 19:44, а я еще на работе. Эта возня с обработкой индексов - единственное, что тормозит новую версию
            self.main.manual_drawing = False
            self.first_center_coords = None
            self.second_center_coords = None
            self.master.capture_button.configure(state = 'disabled')
            if (self.main.data_was_reset or self.main.data_is_external):
                # Иначе индекс становится равным -1
                self.main.data_was_reset = False
                self.main.data_is_external = False # TODO не знаю, нужно ли
            else:
                # Т.к. единственный способ здесь оказаться с какими либо данными (минуя экспорт 
                # или восстановление) - переход из захвата, где после захвата пооследнего 
                # изображения мы лишний раз прибавили 1
                self.main.image_index = max(self.main.image_index - 1, 0)
            
            self.needed_active_pos_monitoring = False
            if (self.angle_thread!= None):
                self.angle_thread.join()
            self.main.is_pause = True
            length = len(self.main.image_data_container) 
            if (length!=0):

                index = self.main.image_index
                # print('index =', index,'; len =', length )
                self.main.image_frame.switchImage(index)
                if (self.main.image_data_container[index].image_has_been_analyzed):
                    self.master.updatePlotAfterAnalysis(index)
                    self.master.updatePrintedDataAfterAnalysis(index)
            else:
                print("image_data_container is empty. What a fluke. \nI''ll do nothing, and you better hope for the best")

                
            # except:
            #     print('error occured during attempt to load modified image in tabHandler')    
            self.main.navigation_frame.next_button.configure(state = 'normal')
            self.main.navigation_frame.prev_button.configure(state = 'normal')
            self.p1 = (0,0)
            self.displayReport()
        elif (self.get() == 'Клиновидность'):
            self.main.navigation_frame.next_button.configure(state = 'disabled')
            self.main.navigation_frame.prev_button.configure(state = 'disabled')
            self.master.capture_button.configure(state = 'disabled')
            self.main.is_pause = False
            self.angle_sec = 0
            self.main.manual_drawing = False
            self.first_center_coords = None
            self.second_center_coords = None

        elif (self.get() == 'Ручной режим'):
            self.main.manual_drawing = True
            self.angle_sec = 0
            self.main.manual_drawing = True # TODO добавил на время разработки фичи
            self.main.navigation_frame.next_button.configure(state = 'disabled')
            self.main.navigation_frame.prev_button.configure(state = 'disabled')
            self.master.capture_button.configure(state = 'disabled')
            self.main.is_pause = False
            self.angle_sec = 0

    def manualySetCoords(self):
        self.angle_sec = self.calculateAngleSec()
        res = self.getParallelismReport()
        self.manual_resultsLabel.configure(text = res)


    def calculateAngleSec(self):
        dist_px  = np.sqrt((self.p0[0]-self.p1[0])**2 + (self.p0[1]-self.p1[1])**2)
        dist_mm = const.PIXEL_TO_MM*dist_px
        base_mm = float(self.base_entry.get())*10

        angle_rad = np.arctan(dist_mm/2/base_mm)/(const.KGW_REFRACTION_INDEX-1)
        angle_sec = angle_rad*180/np.pi*60*60 
        return angle_sec
    
    def getParallelismReport(self):
        return str(int(round(self.angle_sec,0))) + '"'
        
    def angleCalculationWorker(self):
        while self.needed_active_pos_monitoring:
            self.p1 = utility.getCOM(self.main.getImage())
            self.angle_sec = self.calculateAngleSec()

            res = self.getParallelismReport()

            self.resultsLabel.configure(text = res)
            self.main.image_frame.callForCrossesRefresh()
            self.master.update_idletasks()
            time.sleep(0.2)
        print("thread killed (?)")

    def setFirstPosition(self):
        
        self.p0 = utility.getCOM(self.main.getImage())
        # self.needed_active_pos_monitoring = True
    
        self.angle_sec = self.calculateAngleSec()
        # self.getParallelismReport(self.p0, self.p1, self.angle_sec)
        
        res = self.getParallelismReport()
        self.resultsLabel.configure(text = res)
        
        if (not self.needed_active_pos_monitoring):
            self.needed_active_pos_monitoring = True
            self.angle_thread = threading.Thread(target=self.angleCalculationWorker, args=(), daemon=True).start()





    def findMismatches(self , names):

        # set быстрее list, но у меня не так уж много элементов. Возможно удалю 
        # из соображения унификации
        
        names_o = set()
        names_d = set()

        for name in names:
            if name.endswith('_o'):
                names_o.add(name)
            elif name.endswith('_d'):
                names_d.add(name)

        mismatches = []
        
        for name in names_o:
            # достанем имя без суффикса
            base_name = name[:-2]  
            if base_name + '_d' not in names_d:
                mismatches.append(name)

        for name in names_d:
            base_name = name[:-2] 
            if base_name + '_o' not in names_o:
                mismatches.append(name)

        if 'control' in mismatches:
            mismatches.remove('control')
            
        return mismatches


    def analyzeAll(self, data_container):
        
        
        names = []
        for image_data in data_container:
            names.append(image_data.image_name) 
        
        mismatches = self.findMismatches(names)

        if mismatches:
            message = 'Не все измерения имеют пару. Ниже приведены названия несовпадающих:\n'
            for name in mismatches:
                message+=(name + '\n') 

            message+= '\nЕсли не исправить эту проблему, то программа не сможет составить структурированную таблицу, и данные по одному и тому-же кристаллу окажутся в разных строках\n\n'
            message+= 'Продолжить, несмотря на это?'
            answer = messagebox.askquestion(title='Внимание', message=message, )
            if answer == 'no':
                messagebox.showinfo(title = 'Обработка отменена', message = 'Попытайтесь испраить названия и попробуйте снова')
                return
            else:
                self.main.continue_unstructured = True

        self.configure(state = 'disabled')
        self.analyze_all_button.configure(state = 'disabled')
        self.analyze_current_button.configure(state = 'disabled')
        threading.Thread(target=self.analyzeAllWorker, args=(data_container,), daemon=True).start()

    def analyzeAllWorker(self, data_container, any_mismatches = False):
        start = time.time()
        self.main.setProgressBarActive()
        # Костыль, который закрывает баг в nextImage: для начала обработки
        # надо сначала зафиксировать последнее изображение (nextImage), 
        # при этом к индексу картинки автоматически прибавляется 1, 
        # пусть даже следующее изображение не захватывается
        # self.main.navigation_frame.image_index = max(0, self.main.navigation_frame.image_index-1)
        
        # все изображения прошли базовую обработку и имеют полный набор данных (хотелось бы верить)
        self.master.logMessage("Обработка начата...")
        for image_data in data_container:
            if (image_data.image_has_been_analyzed):
                pass
                # text = "Изображение " + name + " уже было проанализировано"
                # self.after(100, self.master.logMessage(text))
            else:

                if (image_data.line_was_built or not image_data.optimisation_needed):
                    
                    image_data.optimisation_needed = False
                    image_data.line_was_built = True
                    
                    image_data.p0_im_space = self.main.image_frame.start_coords
                    image_data.p1_im_space = self.main.image_frame.end_coords

                    crop_x = self.main.crop_factor_x
                    crop_y = self.main.crop_factor_y
                    p0_true = (self.main.image_frame.start_coords[0]/crop_x, self.main.image_frame.start_coords[1]/crop_y)
                    p1_true = (self.main.image_frame.end_coords[0]/crop_x, self.main.image_frame.end_coords[1]/crop_y)

                    image_data.p0_new = p0_true
                    image_data.p1_new = p1_true

                self.main.update_idletasks()
                image_data.analyzeImage(master = self.main)
                name = image_data.image_name
                image_data.image_has_been_analyzed = True
                
                text = "Обработка " + name + " закончена"
                self.after(100, self.master.logMessage(text))
        
        self.main.update_idletasks()
        if self.main.top_level_window != None:
            self.main.top_level_window.destroy()
            self.main.top_level_window.update()
            self.main.top_level_window = None
        self.main.setProgressBarInactive()
        self.main.is_pause = True
        self.after(1000, self.master.logMessage("Все изображения обработаны"))
        self.master.updateWindowAfterAnalysis()
        self.main.files_are_unsaved = True

        self.analyze_all_button.configure(state = 'normal')
        self.analyze_current_button.configure(state = 'normal')
        self.draw_line_checkbox.configure(state = 'disabled')
        self.draw_circle_checkbox.configure(state = 'disabled')
       
        end = time.time()
        time_tot = round(end-start, 1)
        time_avg = time_tot/len(data_container)

        print("Finished in", time_tot, "s. Average time:", time_avg,"s. That wasn''t too shabby, I would say.")


    def selectFramesToAnalyze(self):
        top_level = self.main.top_level_window
        if (top_level != None):
            logging.error('Seems like window already exist')
            return

        self.main.top_level_window = TopLevel(self, self.main.image_data_container)

    
    def sliderEvent(self, val):
        
        self.slider.set(val)
        self.slider2.set(val)
        self.slider3.set(val)
        self.main.image_frame.cam.setExposure(exposure_time_ms = val)

        self.checkForOverexposure()

    def checkForOverexposure(self):
        image_array = np.array(self.main.getImage())
        brightest_pixel_value = np.max(image_array)

        self.max_exposure_label2.configure(text = brightest_pixel_value)
        self.max_exposure_label.configure(text = brightest_pixel_value)

        if (brightest_pixel_value < 250):
            self.slider.configure(button_color = const.FG_COLOR , progress_color= const.PROGRESS_COLOR, button_hover_color = const.HOVER_COLOR)
            self.slider2.configure(button_color = const.FG_COLOR , progress_color= const.PROGRESS_COLOR, button_hover_color = const.HOVER_COLOR)
            self.slider3.configure(button_color = const.FG_COLOR , progress_color= const.PROGRESS_COLOR, button_hover_color = const.HOVER_COLOR)
            
            if self.get() == 'Захват':
                self.master.capture_button.configure(state = 'normal', fg_color = const.FG_COLOR)
            return False
        else:
            # TODO: решил все-же убрать запрет захвата изображения. Возможно, зря
            # self.master.capture_button.configure(state = 'disabled', fg_color = 'red')
            self.slider.configure(button_color = 'red', button_hover_color = 'red', progress_color = 'red' )
            self.slider2.configure(button_color = 'red', button_hover_color = 'red', progress_color = 'red' )
            self.slider3.configure(button_color = 'red', button_hover_color = 'red', progress_color = 'red' )
            
            return True


class App(ctk.CTk):    
    def __init__(self, config):
        super().__init__()
        
        self.config = config
        self.image_index = 0
        self.data_is_external = False   #bool
        self.data_was_reset = False     #bool
        self.photo_is_captured = False  #bool
        self.manual_drawing = True # bool

        self.image_data = None
        
        self.initUI()




    def initUI(self):
        self.image_data_container = []

        self.title("mjolnir")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        height = int(0.8*screen_height)
        width = int(0.8*screen_width)
        self.geometry(f"{width}x{height}")
        
        self.camera_feed_image = None
        try:
            image_path= utility.resourcePath('mockup.tif')        
            self.camera_feed_image = Image.open(image_path).convert('L')
        except Exception as e:
            logging.error(e,stack_info=True, exc_info=True)
            print('Checkout initUI', traceback.format_exc())
            # arr = np.arange(0, screen_width*screen_height, 1, np.uint8)
            arr = np.zeros(1024*1536)
            arr = np.reshape(arr, (1024, 1536))
            self.camera_feed_image = Image.fromarray(arr).convert('L')
            
        self.current_image = self.camera_feed_image


        self.base_path = utility.resourcePath('tmp/')
        current_date = utility.getCurrentDateStr() 
        self.backup_path = self.base_path + current_date + '_tmp/'
        self.organizeBackup() 
        self.backup_folders_names = utility.getBackupFoldersNames(self.base_path)
        self.crop_factor_x = 0
        self.crop_factor_y = 0

        self.files_are_unsaved = False  #bool
        self.is_pause = False   #bool
        self.continue_unstructured = False #bool

        self.setupGrid()

        self.menu = TitleMenu(self)
        self.menu.grid()

        self.top_level_window = None
        self.progress_bar = ctk.CTkProgressBar(self, mode = 'indeterminate',  progress_color="gray10", fg_color = 'gray10')
        # fg_color = 'gray10',
        self.progress_bar.grid(row = 0, column = 0, rowspan = 1, columnspan = 2, sticky = 'nswe', padx = const.DEFAULT_PADX)
        self.progress_bar.set(0)
        
        self.navigation_frame = NavigationFrame(self)
        self.navigation_frame.grid(row=2, column=0, rowspan = 1, sticky="nsew")
        
        self.right_frame = RightFrame(self)
        self.right_frame.grid(row=1, column=1, rowspan = 2, sticky="nsew")
        
        self.image_frame = ImageFrame(self, right_frame_handle= self.right_frame)
        self.image_frame.grid(row=1, column=0, rowspan = 1, sticky="nsew")

        self.widget_list = [self.menu, self.navigation_frame, self.right_frame, self.image_frame]

        self.toggleControl()
        
        
        self.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.mainloop()
    
    def setProgressBarActive(self):
        self.progress_bar.configure(bg_color = const.PROGRESS_BAR_FG_COLOR, progress_color = const.PROGRESS_BAR_PROGRESS_COLOR)
        self.progress_bar.start()

    def setProgressBarInactive(self):
        self.progress_bar.configure(bg_color = 'gray10', progress_color = 'gray10')
        self.progress_bar.stop()

    
    def organizeBackup(self):
        utility.deleteOldFolders(self.base_path)
        utility.createOrCleanFolder(self.backup_path)

    
    def onClosing(self):
        if (self.files_are_unsaved == True):
            answer = messagebox.askyesnocancel(title = 'Внимание', message = "Результаты анализа не были сохранены \nВы хотите сохранить данные перед выходом?",)
            if (answer == True):
                self.menu.exportAll()
            elif(answer == False):
                print('Destroying window...')
                self.image_frame.forgetCamera()
                self.destroy()
        else:
            print('Destroying window...')
            self.image_frame.forgetCamera()
            self.destroy()
            print("Window destroyed, cleanup finished. Wait for this window to close...")
        #     pass
        # # if (self.image_frame cam!= 0):
        # #     try:
        # #         del self.image_frame.cam
        # #     except: 
        # #         print('Possibly there is still no cam object')
        # else:
        #     self.destroy()
        

    def toggleControl(self):
        for widget in self.widget_list:
            widget.toggleControl()

    def setupGrid(self):
        self.grid_columnconfigure(0, weight=2)  
        self.grid_columnconfigure(1, weight=1)  
        self.grid_rowconfigure(0, weight = 0)
        self.grid_rowconfigure(1, weight=1)     
        self.grid_rowconfigure(2, weight = 0)
    
    def getImage(self):
        copy = self.camera_feed_image.copy()
        return copy

    def updateImage(self):
        self.current_image = self.getImage()





# if __name__ == "__main__":
#     # example_function()
    
#     app = App()
