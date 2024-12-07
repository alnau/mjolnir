import numpy as np
import os
import matplotlib.pyplot as plt
import scipy as sp
from scipy.optimize import differential_evolution
import time
import csv

from PIL import Image as img
from PIL import ImageDraw

import utility





pixelToMm = 0.0052

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
    

    def plotBepis(self, image):
        width, height = utility.getSize(image)

        self.p0_new, self.p1_new = utility.getIntersections(self.p0_initial, self.p1_initial, image)

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

        
        self.calculateNumbers(image)


        self.report = utility.getReport(plotname, self.h_width, self.left_side_mm, self.right_side_mm, self.coords_of_max_intensity, self.coords_of_com, self.angle)

        text_data_plt.text(0, 0.8, self.report, transform=text_data_plt.transAxes, fontsize=10, verticalalignment='top')
        for i in range(lenght):
            try:
                brightness = image.getpixel((x_coords_index[i]-1, y_coords_index[i]-1))
                
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
            coord.append(index[i]*pixelToMm)



        img_plt = plt.subplot(121)
        img_plt.axis('off')
        modified_image = self.getModifiedImage(image)
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


    
    def calculateNumbers(self,image):

        width, height = utility.getSize(image)

        brightnessValues = []

        x0 = self.p0_new[0]
        y0 = self.p0_new[1]

        x1 = self.p1_new[0]
        y1 = self.p1_new[1]

        x_coords_index, y_coords_index = utility.bresnanLine(self.p0_new, self.p1_new, width, height)

        lenght = len(x_coords_index) - 1


        for i in range(lenght):
            try:
                brightness = image.getpixel((x_coords_index[i], y_coords_index[i]))
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
            dl = pixelToMm*np.sqrt((x_coords_index[i] - x_coords_index[i+1])**2 + (y_coords_index[i] - y_coords_index[i+1])**2)
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
        self.integral = getIntegral(x0,y0,x1,y1,image)
        

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
        self.coords_of_max_intensity[0] = x_coords_index[max_index]*pixelToMm
        self.coords_of_max_intensity[1] = y_coords_index[max_index]*pixelToMm


        
        self.h_width = (self.right_side_mm - self.left_side_mm)/2
        
        integration_len = 0
        # и координаты центра масс вдоль выбранного направления
        try:
            for i in range(lenght-1):
                dl = np.sqrt((x_coords_index[i] - x_coords_index[i+1])**2 + (y_coords_index[i] - y_coords_index[i+1])**2)
                if (brightnessValues[i]/max_tmp > 0.135):
                    COM_index += integration_len*dl*brightnessValues[i]*(pixelToMm/self.integral)
                integration_len+= dl
        except:
            print("error in COM calculations")
        self.coords_of_com[0] = x_coords_index[int(COM_index)]*pixelToMm
        self.coords_of_com[1] = y_coords_index[int(COM_index)]*pixelToMm
        

    # def visualyVerifyFit(x0,y0,x1,y1,image):
    #     name = image.filename
    #     point0 = (x0,y0)
    #     point1 =  (x1, y1)
        
    #     draw = ImageDraw.Draw(image)
    #     line_color = (255, 255, 255)  
    #     line_width = 2  # Width of the line
    #     draw.line([point0, point1], fill=line_color, width=line_width)

    #     output_path = name + "_modified.tiff"
    #     image.save(output_path)

    #     image.show()

    def getModifiedImage(self,image):
        tmp_image = image

        width, height = utility.getSize(image)
        x0 = self.p0_new[0]
        y0 = self.p0_new[1]

        x1 = self.p1_new[0]
        y1 = self.p1_new[1]

        k = (y1-y0)/(x1-x0)
        b = (y0*x1-y1*x0)/(x1-x0)

        



        point0_new, point1_new = utility.getIntersections(self.p0_new,self.p1_new , image)

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
            
            x0,y0,x1,y1 = optimisation(self.image_name, norm_image)

            self.p0_initial = (x0,y0)
            self.p1_initial = (x1,y1)

            plotname = self.plotBepis(norm_image, name)
            

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
        image = img.open(os.path.join(self.image_path, self.image_name)).convert('L')

        norm_image = utility.normalizeImage(image, self.image_name).convert('L')
        
        x0,y0,x1,y1 = optimisation(self.image_name, norm_image)

        self.p0_initial = (x0,y0)
        self.p1_initial = (x1,y1)

        plotname= self.plotBepis(norm_image)
            
        print(plotname,",",self.h_width)



def getIntegral(x1,y1,x2,y2,image, moment = 0):
        if (x1 == x2 and y1 == y2):
            return -1000000

        width, height = utility.getSize(image)

        brightnessValues = []

        p1 = (x1,y1)
        p2 = (x2,y2)
        
        x_coords_index, y_coords_index = utility.bresnanLine(p1,p2, width, height)
        

        lenght = len(x_coords_index) - 1
        if (lenght == 0):
            return -100000

        for i in range(lenght):
            try:
                brightness  = image.getpixel((x_coords_index[i]-1, y_coords_index[i]-1))
        
                # brightness = pixel[0]
                brightnessValues.append(brightness)
            except:
                print("error in getIntegral")


        integral = 0
        maximum = max(brightnessValues)
        len_along_the_line = 0
        for i in range(lenght-1):
            try:
                deltaLineCoord = pixelToMm*np.sqrt((x_coords_index[i]-x_coords_index[i+1])**2 + (y_coords_index[i] - y_coords_index[i+1])**2)
                # if (brightnessValues[i]/maximum > 0.135):
                if (moment == 0):
                    # if (brightnessValues[i]/maximum > 0.05):
                    integral += brightnessValues[i]*deltaLineCoord
                else:
                    integral += brightnessValues[i]*deltaLineCoord*len_along_the_line**moment
                    len_along_the_line+=deltaLineCoord
            except:
                print("error in integral; i=", i, "length-1 =", lenght - 1)
        # print(integral)
        return integral

def funcToOptimize(args,image, RMS = True):
    x0,y0,x1,y1 = map(int, args)
    if (RMS):
        norm = 1.0/getIntegral(x0,y0,x1,y1,image)
        dispersion = norm*getIntegral(x0,y0,x1,y1,image, moment=2) - (norm**2)*getIntegral(x0,y0,x1,y1,image, moment = 1)**2

        return - np.sqrt(max(dispersion,0))
    else:
        return -getIntegral(x0,y0,x1,y1,image)

def optimisation(image_name, image):
    
    print("optimisation on", image_name, " has been started")
    trial_image = utility.thresholdImage(image, 0.12)
    start = time.time()
    width,height = utility.getSize(trial_image)
    bounds = [[0, width-1], [0,height-1], [0, width-1], [0,height-1]]
    result = differential_evolution(lambda args: funcToOptimize(args, trial_image, RMS=False), bounds)
    x0_initial, y0_initial, x1_initial, y1_initial = map(int, result.x)
    
    # image_data.p0_initial[0] = x0_initial
    # image_data.p0_initial[0] = y0_initial

    # image_data.p1_initial[0] = x1_initial
    # image_data.p1_initial[0] = y1_initial


    bestVal = result.fun
    end = time.time()
    # print(best_x0,best_y0,best_x1, best_y1)
    print("gotcha. By the way, it took", "{:.1f}".format(end-start),"s")
    return x0_initial, y0_initial, x1_initial, y1_initial



