import numpy as np
import os
import matplotlib.pyplot as plt
import time
import csv

from PIL import Image as img
from PIL import ImageDraw

import utility

from constants import *







class ImageData():

    def __init__(self, original_image, name = None):
        self.image_name = name

        tmp_image = original_image.copy()

        self.initial_image = tmp_image.convert('L')
        self.norm_image = utility.normalizeImage(self.initial_image, self.image_name).convert('L')
        self.modified_image = 0

        self.coords_of_max_intensity = [0,0]
        self.coords_of_com = [0,0]
        self.left_side_mm = 0
        self.right_side_mm = 0
        self.h_width = 0

        self.optimisation_needed = True
        self.image_has_been_analysed = False

        self.report = ''

        self.integral = 0

        self.brightness_values = []
        self.normalised_brightness_values = []
        self.coord = []

        self.plotname = ''


        self.p0_initial = (0,0)
        self.p1_initial = (0,0)

        self.p0_new = (0,0)
        self.p1_new = (0,0)
    

    def calculateNumbers(self):

        
        width, height = utility.getSize(self.initial_image)

        if (self.optimisation_needed):
            self.p0_new, self.p1_new = utility.getIntersections(self.p0_initial, self.p1_initial, self.initial_image)


        x0 = self.p0_new[0]
        y0 = self.p0_new[1]

        x1 = self.p1_new[0]
        y1 = self.p1_new[1]

        x_coords_index, y_coords_index = utility.bresnanLine(self.p0_new, self.p1_new, width, height)

        lenght = len(x_coords_index) - 1


        for i in range(lenght):
            try:
                brightness = self.norm_image.getpixel((x_coords_index[i], y_coords_index[i]))
 
                # Какой-то странный баг выплевывает интенсивности 255 там, где их быть не может быть.
                # пахнет немытыми костылями

                # костыли не сработали, ищи нормальное решение

                # Господи, ты такой идиот. Ты охуительно выстрелил себе в ногу. 
                # После чего ты решил высадить полный магазин в свежую рану, лишь для того, 
                # чтобы понять, что боль была от твоих же действий

                self.brightness_values.append(brightness)
            except:
                # print("ERROR in brightness", image.getpixel((x_coords_index[i]-1, y_coords_index[i]-1)))
                print("ERROR in brightness")

        len_of_line = 0
        self.coord.append(0)
        for i in range(lenght-1):
            dl = PIXEL_TO_MM*np.sqrt((x_coords_index[i] - x_coords_index[i+1])**2 + (y_coords_index[i] - y_coords_index[i+1])**2)
            self.coord.append(len_of_line)
            len_of_line+=dl

        still_searching_for_max = True

        try:
            self.maximum = max(self.brightness_values)
        except:
            print(x0,y0,x1,y1)
            print(self.brightness_values)
        max_tmp = 0
        max_index = 0
        
        for i in range(lenght):
            if (self.brightness_values[i] > max_tmp):
                max_tmp = self.brightness_values[i]
                max_index = i
            self.normalised_brightness_values.append(self.brightness_values[i]/self.maximum)
        
        if (self.maximum != max_tmp):
            print("Calculated maximum not equal to max()")

        COM_index = 0
        self.integral = utility.getIntegral(x0,y0,x1,y1,self.norm_image)
        

        # Найдем полуширину и максимум интенсивности
        for i in range(lenght-1):
            try:
                if (still_searching_for_max):
                    if (self.brightness_values[i]/self.maximum < 0.135):
                        self.left_side_mm = self.coord[i]
                    else:
                        still_searching_for_max = False
                elif (self.brightness_values[i]/self.maximum >= 0.135):
                    self.right_side_mm = self.coord[i]
            except:
                print("error in max intensity; i =", i, "len =", lenght) 
        self.coords_of_max_intensity[0] = x_coords_index[max_index]*PIXEL_TO_MM
        self.coords_of_max_intensity[1] = y_coords_index[max_index]*PIXEL_TO_MM

        self.modified_image = self.getModifiedImage()

        self.h_width = (self.right_side_mm - self.left_side_mm)/2
        
        integration_len = 0
        # и координаты центра масс вдоль выбранного направления
        try:
            for i in range(lenght-1):
                dl = np.sqrt((x_coords_index[i] - x_coords_index[i+1])**2 + (y_coords_index[i] - y_coords_index[i+1])**2)
                if (self.brightness_values[i]/max_tmp > 0.135):
                    COM_index += integration_len*dl*self.brightness_values[i]*(PIXEL_TO_MM/self.integral)
                integration_len+= dl
        except:
            print("error in COM calculations")
        self.coords_of_com[0] = x_coords_index[int(COM_index)]*PIXEL_TO_MM
        self.coords_of_com[1] = y_coords_index[int(COM_index)]*PIXEL_TO_MM

        try:
            _, tail= os.path.split(self.image_name)
            plotname, _ = os.path.splitext(tail)
        except:
            print("Problems occured during name formatting")
            self.image_name = 'none'
            plotname = 'none'
        self.angle = np.degrees(np.arctan(np.abs((self.p1_new[1]-self.p0_new[1])/(self.p1_new[0]-self.p0_new[0]))))

        self.report = utility.getReport(plotname, self.h_width, self.left_side_mm, self.right_side_mm, self.coords_of_max_intensity, self.coords_of_com, self.angle)



    def plotBepis(self):
        
        width, height = utility.getSize(self.initial_image)
        
        plt.tight_layout(pad=0)
        plt.figure(figsize=(12.1, 4.8))

        text_data_plt = plt.subplot(224)
        text_data_plt.axis('off')

        text_data_plt.text(0, 0.8, self.report, transform=text_data_plt.transAxes, fontsize=10, verticalalignment='top')        

        img_plt = plt.subplot(121)
        img_plt.axis('off')
        modified_image = self.getModifiedImage()
        img_plt.imshow(modified_image)

        
        line_plt = plt.subplot(222)
        line_plt.plot(self.coord, self.brightness_values)
        line_plt.axhline(y = 0.135, color = 'r', linestyle = '--', linewidth = 2)
        # line_plt.axvline(x = left_side_mm, color = 'r', linestyle = '--', linewidth = 2)
        # line_plt.axvline(x = right_side_mm, color = 'r', linestyle = '--', linewidth = 2) 
        # print(brightness_values)
        # plt.show()
        
        plotname_updated = "lastResults/" + self.plotname + "_plot.png"
        plt.savefig(plotname_updated)


    
    

    def getModifiedImage(self):
        tmp_image = self.norm_image.copy()

        width, height = utility.getSize(self.initial_image)
        x0 = self.p0_new[0]
        y0 = self.p0_new[1]

        x1 = self.p1_new[0]
        y1 = self.p1_new[1]

        k = (y1-y0)/(x1-x0)
        b = (y0*x1-y1*x0)/(x1-x0)

        draw = ImageDraw.Draw(tmp_image)

        # print(point0, point1)

        line_color = 255  
        line_width = 2  # Width of the line
        draw.line([self.p0_new, self.p1_new], fill = line_color, width = line_width)

        return tmp_image

    def analyseImage(self):
        
        print("Optimisation needed = ", self.optimisation_needed)
        
        if (self.optimisation_needed):
            x0,y0,x1,y1 = utility.optimisation(self.image_name, self.norm_image)
            self.p0_initial = (x0,y0)
            self.p1_initial = (x1,y1)
        else:
            self.p0_new = self.p0_initial
            self.p1_new = self.p1_initial

        self.calculateNumbers()

        # self.plotBepis(optimisation_needed)



    
    # def analyseAll(self):
    #     path = image.path
    #     names = []
    #     for image_name in os.listdir(path):
    #         if (image_name.endswith(".tif")):
    #             names.append(image_name)

        
    #     new_names = []
    #     width_data_d = []
    #     width_data_o = []
    #     for name in names:
            
    #         image = img.open(os.path.join(path, name)).convert('L')

    #         norm_image = utility.normalizeImage(image, name).convert('L')
            
    #         x0,y0,x1,y1 = utility.optimisation(self.image_name, norm_image)

    #         self.p0_initial = (x0,y0)
    #         self.p1_initial = (x1,y1)

    #         plotname = self.plotBepis(name)
            

    #         number, _ , test_for_d_o = plotname.partition("_")
            
            
    #         if (test_for_d_o == "d"):
    #             width_data_d.append(self.h_width)
    #             new_names.append(number)
    #         elif (test_for_d_o == "o"):
    #             width_data_o.append(self.h_width)
    #         image.close()
    #         norm_image.close()

    #         print("------------------")
        
    #     # integral = getIntegral(x0,y0,x1,y1,image)
    #     if (len(new_names)!=len(width_data_d) or len(new_names)!=len(width_data_o) ):
    #         print("error with files")
        
    #     utility.printReportToCSV(new_names, width_data_d, width_data_o)


    # def analyseFile(self):
    #     self.initial_image = img.open(os.path.join(self.image_path, self.image_name)).convert('L')

    #     norm_image = utility.normalizeImage(self.initial_image, self.image_name).convert('L')
        
    #     x0,y0,x1,y1 = utility.optimisation(self.image_name, norm_image)

    #     self.p0_initial = (x0,y0)
    #     self.p1_initial = (x1,y1)

    #     plotname= self.plotBepis()



