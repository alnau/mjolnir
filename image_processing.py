import numpy as np
import os
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import time
import csv
from scipy.stats import norm


from PIL import Image as img
from PIL import ImageDraw

import logging

import utility
from constants import *




class ImageData():

    def __init__(self, original_image, name = None):
        self.image_name = name

        tmp_image = original_image.copy()

        self.initial_image = tmp_image.convert('L')
        self.norm_image = utility.normalizeImage(self.initial_image).convert('L')
        # self.modified_image = self.getModifiedImage()
        self.modified_image = 0

        self.width, self.height = utility.getSize(self.norm_image)
        self.coords_of_max_intensity = [0,0]
        self.coords_of_com = [0,0]
        self.left_side_mm = 0
        self.right_side_mm = 0
        self.h_width = 0
        self.radius_mm = 0
        self.parallelism_angle_s = 0

        self.line_was_built = False
        self.radius_was_calculated = False
        self.parallelism_has_been_calculated = False

        self.optimisation_needed = True
        self.image_has_been_analysed = False

        self.report = ''

        self.integral = 0

        self.brightness_values = []
        self.normalized_brightness_values = []
        self.coord = []


        self.plotname = name

        self.p0_initial = (0,0)
        self.p1_initial = (0,0)

        self.p0_new = (0,0)
        self.p1_new = (0,0)

        self.p0_im_space = (0,0)
        self.p1_im_space = (0,0)
    
    def getCOM(self):
        arr_image = np.array(self.norm_image)
        arr_image[arr_image < CUTOFF_THRESHOLD] = 0

        x = np.sum(np.sum(arr_image, axis=0) * np.arange(self.width)) / np.sum(arr_image)
        y = np.sum(np.sum(arr_image, axis=1) * np.arange(self.height)) / np.sum(arr_image)
        com = (int(x),int(y))
        return com
    
    def getRMax(self, p_com):
        rx = min(p_com[0], self.width - p_com[0])-1
        ry = min(p_com[1], self.height - p_com[1]) - 1

        return min(rx,ry)

    def getSupRMax(self, p_com):
        rx = max(p_com[0], self.width - p_com[0]) -1 
        ry = max(p_com[1], self.height - p_com[1]) - 1

        return max(rx,ry)
    


    def getRadius(self):
        print('Radius evaluation algorithm has been initiated...')
        print('Damned math inbound! \n(god save our souls)')
        start = time.time()

        com_xy = self.getCOM()
        self.coords_of_com[0] = com_xy[0]*PIXEL_TO_MM
        self.coords_of_com[1] = com_xy[1]*PIXEL_TO_MM

        r_max = self.getRMax(com_xy)

        full_integral, error_full_integral = utility.integrateOverPolar(self.norm_image, com_xy[0], com_xy[1], r_max)

        radius_mm = 0

        radius_px = self.binarySearch(2, com_xy, r_max, full_integral)
        end = time.time()
        radius_mm = radius_px*PIXEL_TO_MM
        print('That wasn''t too hard, but, man, it still hurts. Time per execution =', '{:.1f}'.format(end-start),'s')

        return radius_mm

    def binarySearch(self, epsilon, com, r_max, full_integral):
        r0 = 0
        r1 = r_max


        left_val = 0
        integral_tmp, _ = utility.integrateOverPolar(self.norm_image, com[0],  com[1], r1) 
        right_val = integral_tmp/full_integral - ENERGY_THRESHOLD
        intermediate_val = 0
        iter_counter = 0
        while ((r1-r0)/2 >= epsilon and iter_counter < 10):
            r_inter = (r1+r0)/2

            integral_tmp, _ =  utility.integrateOverPolar(self.norm_image, com[0],  com[1], r_inter)
            intermediate_val = integral_tmp/full_integral - ENERGY_THRESHOLD

            if (right_val*intermediate_val < 0):
                # величины меняют знак => ноль между ними
                r0 = r_inter
            else:
                r1 = r_inter
                
            iter_counter+=1
        return (r1+r0)/2
        

    def verification(self, radius):
        print('verification started, grab a beer, it may take a while...')
        start = time.time()
        I_in = 0
        I_sum = 0
        com = (self.coords_of_com[0]/PIXEL_TO_MM, self.coords_of_com[1]/PIXEL_TO_MM)
        for ix in range(self.width):
            for iy in range(self.height):
                if ((com[0]-ix)**2+(com[1] - iy)**2 < self.getRMax(com)**2):
                    brightness = self.norm_image.getpixel((ix,iy))
                    I_sum+=brightness
                    if ((com[0]-ix)**2+(com[1] - iy)**2 < radius**2):
                        I_in+=brightness
        end = time.time()

        print(I_in/I_sum, ";", end-start,"s")

    

    def calculateNumbers(self):
        if (self.optimisation_needed):
            self.p0_new, self.p1_new = utility.getIntersections(self.p0_initial, self.p1_initial, self.initial_image)
            self.line_was_built = True

        x0 = self.p0_new[0]
        y0 = self.p0_new[1]

        x1 = self.p1_new[0]
        y1 = self.p1_new[1]

        x_coords_index, y_coords_index = utility.bresenhamLine(self.p0_new, self.p1_new, self.width, self.height)

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

                # (upd + ~1w, чисто для истории) Ты анализировал изображение, на котором ты успел нарисовать линию
                self.brightness_values.append(brightness)
            except Exception as e:
                logging.error("Error in Brightness:", e)
                # print("ERROR in brightness", image.getpixel((x_coords_index[i]-1, y_coords_index[i]-1)))
                print("ERROR in brightness")

        len_of_line = 0
        self.coord.append(0)
        # TODO: Перевести на np.array и соответствующие методы обработки
        for i in range(lenght-1):
            dl = PIXEL_TO_MM*np.sqrt((x_coords_index[i] - x_coords_index[i+1])**2 + (y_coords_index[i] - y_coords_index[i+1])**2)
            self.coord.append(len_of_line)
            len_of_line+=dl

        still_searching_for_max = True

        self.maximum = 0
        try:
            self.maximum = max(self.brightness_values)
        except Exception as e:
            logging.error(e, '\n', 'initial points: ', self.p0_initial, self.p1_initial, '\n', 'new: ', self.p0_new, self.p1_new)
            print('initial points: ', self.p0_initial, self.p1_initial)
            print('new: ', self.p0_new, self.p1_new)
            print(self.brightness_values)
        
        max_tmp = 0
        max_index = 0
        for i in range(lenght):
            if (self.brightness_values[i] > max_tmp):
                max_tmp = self.brightness_values[i]
                max_index = i

        if (self.maximum != max_tmp):
            print("Calculated maximum not equal to max()")
        
        
        self.maximum = max_tmp

        for i in range(lenght):
            self.normalized_brightness_values.append(self.brightness_values[i]/self.maximum)
        
        self.integral = utility.getIntegral(x0,y0,x1,y1,self.norm_image)

        # Найдем полуширину и максимум интенсивности
        for i in range(lenght-1):
            try:
                if (still_searching_for_max):
                    if (self.brightness_values[i]/self.maximum < 1-ENERGY_THRESHOLD):
                        self.left_side_mm = self.coord[i]
                    else:
                        still_searching_for_max = False
                elif (self.brightness_values[i]/self.maximum >= 1 - ENERGY_THRESHOLD):
                    self.right_side_mm = self.coord[i]
            except Exception as e:
                logging.error('msg:', e, '\n', "error in max intensity; i =", i, "len =", lenght)
                print("error in max intensity; i =", i, "len =", lenght) 
        
        
        self.coords_of_max_intensity[0] = x_coords_index[max_index]*PIXEL_TO_MM
        self.coords_of_max_intensity[1] = y_coords_index[max_index]*PIXEL_TO_MM

        self.radius_mm = self.getRadius()
        self.radius_was_calculated = True

        

        self.modified_image = self.getModifiedImage()

        self.h_width = (self.right_side_mm - self.left_side_mm)/2
        
        try:
            _, tail= os.path.split(self.image_name)
            plotname, _ = os.path.splitext(tail)
        except Exception as e:
            logging.error("Problems occured during name formatting;", e)
            print("Problems occured during name formatting")
            self.image_name = 'none'
            plotname = 'none'
        self.angle = np.degrees(np.arctan(np.abs((self.p1_new[1]-self.p0_new[1])/(self.p1_new[0]-self.p0_new[0]))))
        if (self.parallelism_has_been_calculated):
            self.report = utility.getReport(plotname, self.radius_mm, 
                                            self.h_width, self.left_side_mm, 
                                            self.right_side_mm, self.coords_of_max_intensity, 
                                            self.coords_of_com, self.angle, self.parallelism_angle_s)
        else:
            self.report = utility.getReport(plotname, self.radius_mm, 
                                            self.h_width, self.left_side_mm, 
                                            self.right_side_mm, self.coords_of_max_intensity, 
                                            self.coords_of_com, self.angle)



    def plotBepis(self, path = ''):
        
        plt.tight_layout(pad=0)
        plt.figure(figsize=(12.1, 4.8))

        text_data_plt = plt.subplot(224)
        text_data_plt.axis('off')

        text_data_plt.text(0, 0.8, self.report, transform=text_data_plt.transAxes, fontsize=10, verticalalignment='top')        

        img_plt = plt.subplot(121)
        img_plt.axis('off')
        # modified_image = self.getModifiedImage()
        img_plt.imshow(self.modified_image)

        
        line_plt = plt.subplot(222)
        line_plt.plot(self.coord, self.brightness_values)
        
        filename = self.plotname + "_plot.png"
        if (path == ''):
            plot_path_rel = "lastResults/" + filename
            plot_path = utility.resourcePath(plot_path_rel)
        else:
            plot_path = os.path.join(path, filename)
        plt.savefig(plot_path)
        plt.close()




    def getModifiedImage(self):
        tmp_image = self.norm_image.copy()

        x0 = self.p0_new[0]
        y0 = self.p0_new[1]

        x1 = self.p1_new[0]
        y1 = self.p1_new[1]

        k = (y1-y0)/(x1-x0)
        b = (y0*x1-y1*x0)/(x1-x0)

        draw = ImageDraw.Draw(tmp_image)

        line_color = 255  
        line_width = 1  # Width of the line
        # draw.line([self.p0_new, self.p1_new], fill = line_color, width = line_width)
        circle_radius = int(self.radius_mm/PIXEL_TO_MM)
        start_coords = (int(self.coords_of_com[0]/PIXEL_TO_MM),int(self.coords_of_com[1]/PIXEL_TO_MM))
        draw.ellipse(utility.getCircleBound(start_coords, circle_radius), outline = line_color, width = line_width)

        return tmp_image

    def analyseImage(self):
        
        ZERO = (0,0)
        if (self.p0_initial == ZERO or self.p1_initial == ZERO):
            self.optimisation_needed = True

        print("Optimisation needed = ", self.optimisation_needed)
        
        if (self.optimisation_needed):
            x0,y0,x1,y1 = utility.optimisation(self.image_name, self.norm_image)
            self.p0_initial = (x0,y0)
            self.p1_initial = (x1,y1)
        else:
            self.p0_new = self.p0_initial
            self.p1_new = self.p1_initial

        self.calculateNumbers()


    
def analyseAll(path, _start = 0):
    # path = image.path
    names = []
    for image_name in os.listdir(path):
        if (image_name.endswith(".tif")):
            names.append(image_name)
    
    new_names = []
    width_data_d = []
    width_data_o = []
    counter = 0

    start = time.time()
    d_ref = 0
    
    for name in names:
        if (counter < _start):
            counter+=1
            continue
        image = img.open(os.path.join(path, name)).convert('L')
        
        pure_name,_ = name.split('.')
        image_data = ImageData(image, pure_name)
        
        image_data.analyseImage()
        image_data.plotBepis()
        
        if (image_data.plotname!='control'):
            number, test_for_d_o = image_data.plotname.rsplit("_",1)
        
            if (test_for_d_o == "d"):
                width_data_d.append(2*image_data.radius_mm)
                new_names.append(number)
            elif (test_for_d_o == "o"):
                width_data_o.append(2*image_data.radius_mm)
            image.close()
        elif (image_data.plotname == 'control'):
            d_ref = 2*image_data.radius_mm
        print("------------------")

    if (len(new_names)!=len(width_data_d) or len(new_names)!=len(width_data_o) ):
        print("error with files")
    
    num_of_images = len(names)
    utility.printReportToCSV(new_names, width_data_d, width_data_o)
    utility.printReportToXLSX(new_names, width_data_d, width_data_o, d_ref)
    end = time.time()

    print("So whole journey took about", '{:.1f}'.format(end-start), 's. That''s about', '{:.1f}'.format((end-start)/num_of_images), 's per image. \nNot too shaby at all')


def analyseFile(path,name):
        image = img.open(os.path.join(path, name)).convert('L')
        pure_name,_ = name.split('.')
        image_data = ImageData(image, pure_name)
        
        image_data.analyseImage()
        image_data.plotBepis()

        number, _ , test_for_d_o = image_data.plotname.partition("_")
        
        image.close()




