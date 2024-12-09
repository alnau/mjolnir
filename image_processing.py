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

    def __init__(self,image_path,  name):
        self.image_path = image_path
        self.image_name = name
        
        self.coords_of_max_intensity = [0,0]
        self.coords_of_com = [0,0]
        self.left_side_mm = 0
        self.right_side_mm = 0
        self.h_width = 0

        self.report = ''

        self.integral = 0



        self.p0_initial = (0,0)
        self.p1_initial = (0,0)

        self.p0_new = (0,0)
        self.p1_new = (0,0)
    

    def plotBepis(self):
        
        width, height = utility.getSize(self.initial_image)

        self.p0_new, self.p1_new = utility.getIntersections(self.p0_initial, self.p1_initial, self.initial_image)

        _, tail= os.path.split(self.image_name)
        plotname, _ = os.path.splitext(tail)

        plt.tight_layout(pad=0)
        plt.figure(figsize=(12.1, 4.8))
        
        self.angle = np.degrees(np.arctan(np.abs((self.p1_new[1]-self.p0_new[1])/(self.p1_new[0]-self.p0_new[0]))))

        brightnessValues = []

        x_coords_index, y_coords_index = utility.bresnanLine(self.p0_new, self.p1_new, width, height)
        lenght = len(x_coords_index) - 1

        text_data_plt = plt.subplot(224)
        text_data_plt.axis('off')

        
        self.calculateNumbers()


        self.report = utility.getReport(plotname, self.h_width, self.left_side_mm, self.right_side_mm, self.coords_of_max_intensity, self.coords_of_com, self.angle)

        text_data_plt.text(0, 0.8, self.report, transform=text_data_plt.transAxes, fontsize=10, verticalalignment='top')
        for i in range(lenght):
            try:
                brightness = self.initial_image.getpixel((x_coords_index[i]-1, y_coords_index[i]-1))
                
                # brightness = pixel[0]
                brightnessValues.append(brightness)
            except:
                print("ERROR in brightness")

        maximum = max(brightnessValues)
        index = np.arange(lenght)
        coord = []
        for i in range(lenght):
            brightnessValues[i] = brightnessValues[i]/maximum 
            # print(brightnessValues[i])
            coord.append(index[i]*PIXEL_TO_MM)



        img_plt = plt.subplot(121)
        img_plt.axis('off')
        modified_image = self.getModifiedImage()
        img_plt.imshow(modified_image)

        
        line_plt = plt.subplot(222)
        line_plt.plot(coord, brightnessValues)
        line_plt.axhline(y = 0.135, color = 'r', linestyle = '--', linewidth = 2)
        # line_plt.axvline(x = left_side_mm, color = 'r', linestyle = '--', linewidth = 2)
        # line_plt.axvline(x = right_side_mm, color = 'r', linestyle = '--', linewidth = 2) 
        # print(brightnessValues)
        # plt.show()
        
        plotname_updated = "lastResults/" + plotname + "_plot.png"
        plt.savefig(plotname_updated)

        return plotname


    
    def calculateNumbers(self):

        width, height = utility.getSize(self.initial_image)

        brightnessValues = []

        x0 = self.p0_new[0]
        y0 = self.p0_new[1]

        x1 = self.p1_new[0]
        y1 = self.p1_new[1]

        x_coords_index, y_coords_index = utility.bresnanLine(self.p0_new, self.p1_new, width, height)

        lenght = len(x_coords_index) - 1


        for i in range(lenght):
            try:
                brightness = self.initial_image.getpixel((x_coords_index[i], y_coords_index[i]))
                # brightness = pixel[0]
                # print(pixel[0])
    
                # if (brightness == 255):
                #     print("error with brightness. Coordinates:", x_coords_index[i]-1, y_coords_index[i]-1)

                # Какой-то странный баг выплевывает интенсивности 255 там, где их быть не может быть.
                # пахнет немытыми костылями

                # костыли не сработали, ищи нормальное решение

                # Господи, ты такой идиот. Ты охуительно выстрелил себе в ногу. 
                # После чего ты решил высадить полный магазин в свежую рану, лишь для того, 
                # чтобы понять, что боль была от твоих же действий

                brightnessValues.append(brightness)
            except:
                # print("ERROR in brightness", image.getpixel((x_coords_index[i]-1, y_coords_index[i]-1)))
                print("ERROR in brightness")

        coord = []
        len_of_line = 0
        for i in range(lenght-1):
            dl = PIXEL_TO_MM*np.sqrt((x_coords_index[i] - x_coords_index[i+1])**2 + (y_coords_index[i] - y_coords_index[i+1])**2)
            coord.append(len_of_line)
            len_of_line+=dl

        still_searching_for_max = True

        try:
            maximum = max(brightnessValues)
        except:
            print(x0,y0,x1,y1)
            print(brightnessValues)
        max_tmp = 0
        max_index = 0
        
        for i in range(lenght):
            if (brightnessValues[i] > max_tmp):
                max_tmp = brightnessValues[i]
                max_index = i
        
        if (maximum != max_tmp):
            print("Calculated maximum not equal to max()")

        COM_index = 0
        self.integral = utility.getIntegral(x0,y0,x1,y1,self.initial_image)
        

        # Найдем полуширину и максимум интенсивности
        for i in range(lenght-1):
            try:
                if (still_searching_for_max):
                    if (brightnessValues[i]/maximum < 0.135):
                        self.left_side_mm = coord[i]
                    else:
                        still_searching_for_max = False
                elif (brightnessValues[i]/maximum >= 0.135):
                    self.right_side_mm = coord[i]
            except:
                print("error in max intensity; i =", i, "len =", lenght) 
        self.coords_of_max_intensity[0] = x_coords_index[max_index]*PIXEL_TO_MM
        self.coords_of_max_intensity[1] = y_coords_index[max_index]*PIXEL_TO_MM


        
        self.h_width = (self.right_side_mm - self.left_side_mm)/2
        
        integration_len = 0
        # и координаты центра масс вдоль выбранного направления
        try:
            for i in range(lenght-1):
                dl = np.sqrt((x_coords_index[i] - x_coords_index[i+1])**2 + (y_coords_index[i] - y_coords_index[i+1])**2)
                if (brightnessValues[i]/max_tmp > 0.135):
                    COM_index += integration_len*dl*brightnessValues[i]*(PIXEL_TO_MM/self.integral)
                integration_len+= dl
        except:
            print("error in COM calculations")
        self.coords_of_com[0] = x_coords_index[int(COM_index)]*PIXEL_TO_MM
        self.coords_of_com[1] = y_coords_index[int(COM_index)]*PIXEL_TO_MM


    def getModifiedImage(self):
        tmp_image = self.initial_image

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
    
    def analyseAll(self):
        path = image.path
        names = []
        for image_name in os.listdir(path):
            if (image_name.endswith(".tif")):
                names.append(image_name)

        
        new_names = []
        width_data_d = []
        width_data_o = []
        for name in names:
            
            image = img.open(os.path.join(path, name)).convert('L')

            norm_image = utility.normalizeImage(image, name).convert('L')
            
            x0,y0,x1,y1 = utility.optimisation(self.image_name, norm_image)

            self.p0_initial = (x0,y0)
            self.p1_initial = (x1,y1)

            plotname = self.plotBepis(name)
            

            number, _ , test_for_d_o = plotname.partition("_")
            
            
            if (test_for_d_o == "d"):
                width_data_d.append(self.h_width)
                new_names.append(number)
            elif (test_for_d_o == "o"):
                width_data_o.append(self.h_width)
            image.close()
            norm_image.close()

            print("------------------")
        
        # integral = getIntegral(x0,y0,x1,y1,image)
        if (len(new_names)!=len(width_data_d) or len(new_names)!=len(width_data_o) ):
            print("error with files")
        
        utility.printReportToCSV(new_names, width_data_d, width_data_o)


    def analyseFile(self):
        self.initial_image = img.open(os.path.join(self.image_path, self.image_name)).convert('L')

        norm_image = utility.normalizeImage(self.initial_image, self.image_name).convert('L')
        
        x0,y0,x1,y1 = utility.optimisation(self.image_name, norm_image)

        self.p0_initial = (x0,y0)
        self.p1_initial = (x1,y1)

        plotname= self.plotBepis()







