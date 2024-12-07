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



def plotBepis(x0, y0, x1, y1, image, name):
    width, height = utility.getSize(image)

    point0_new, point1_new = utility.getIntersections((x0,y0), (x1,y1), image)

    _, tail= os.path.split(name)
    plotname, _ = os.path.splitext(tail)

    plt.tight_layout(pad=0)
    plt.figure(figsize=(12.1, 4.8))
    
    angle = np.degrees(np.arctan(np.abs((y1-y0)/(x1-x0))))

    brightnessValues = []

    x_coords_index, y_coords_index = utility.bresnanLine(point0_new[0], point0_new[1], point1_new[0], point1_new[1], width, height)
    lenght = len(x_coords_index) - 1

    text_data_plt = plt.subplot(224)
    text_data_plt.axis('off')

    coords_of_max_intensity = [0,0]
    coords_of_com = [0,0]
    left_side_mm = 0
    right_side_mm = 0
    h_width, left_side_mm, right_side_mm, coords_of_max_intensity, coords_of_com = getNumbers(point0_new[0], point0_new[1], point1_new[0], point1_new[1],image)


    report = utility.getReport(plotname, h_width, left_side_mm, right_side_mm, coords_of_max_intensity, coords_of_com, angle)

    text_data_plt.text(0, 0.8, report, transform=text_data_plt.transAxes, fontsize=10, verticalalignment='top')
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
    modified_image = getModifiedImage(x_coords_index[0],y_coords_index[0],x_coords_index[lenght],y_coords_index[lenght],image)
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

    return plotname, h_width


def getIntegral(x1,y1,x2,y2,image, moment = 0):
    if (x1 == x2 and y1 == y2):
        return -1000000

    width, height = utility.getSize(image)

    brightnessValues = []
    
    x_coords_index, y_coords_index = utility.bresnanLine(x1, y1, x2, y2, width, height)
    

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

def optimisation(image, name):
    
    print("optimisation on", name, " has been started")
    trial_image = utility.thresholdImage(image, 0.12)
    start = time.time()
    width,height = utility.getSize(trial_image)
    bounds = [[0, width-1], [0,height-1], [0, width-1], [0,height-1]]
    result = differential_evolution(lambda args: funcToOptimize(args,trial_image, RMS=False), bounds)
    best_x0, best_y0, best_x1, best_y1 = map(int, result.x)
    bestVal = result.fun
    end = time.time()
    # print(best_x0,best_y0,best_x1, best_y1)
    print("gotcha. By the way, it took", "{:.1f}".format(end-start),"s")
    return best_x0, best_y0, best_x1, best_y1, bestVal

def getNumbers(x0,y0,x1,y1,image):

    width, height = utility.getSize(image)

    brightnessValues = []

    x_coords_index, y_coords_index = utility.bresnanLine(x0, y0, x1, y1, width, height)

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

    left_side = 0
    right_side = 0
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
    coords_of_max_intensity = [0,0]
    coords_of_COM = [0,0]
    COM_index = 0
    integral = getIntegral(x0,y0,x1,y1,image)
     

    # Найдем полуширину и максимум интенсивности
    for i in range(lenght-1):
        try:
            if (still_searching_for_max):
                if (brightnessValues[i]/maximum < 0.135):
                    left_side = coord[i]
                else:
                    still_searching_for_max = False
            elif (brightnessValues[i]/maximum >= 0.135):
                right_side = coord[i]
        except:
            print("error in max intensity; i =", i, "len =", lenght) 
    coords_of_max_intensity[0] = x_coords_index[max_index]*pixelToMm
    coords_of_max_intensity[1] = y_coords_index[max_index]*pixelToMm


    
    w = (right_side - left_side)/2
    
    integration_len = 0
    # и координаты центра масс вдоль выбранного направления
    try:
        for i in range(lenght-1):
            dl = np.sqrt((x_coords_index[i] - x_coords_index[i+1])**2 + (y_coords_index[i] - y_coords_index[i+1])**2)
            if (brightnessValues[i]/max_tmp > 0.135):
                COM_index += integration_len*dl*brightnessValues[i]*(pixelToMm/integral)
            integration_len+= dl
    except:
        print("error in COM calculations")
    coords_of_COM[0] = x_coords_index[int(COM_index)]*pixelToMm
    coords_of_COM[1] = y_coords_index[int(COM_index)]*pixelToMm
    return w, left_side, right_side, coords_of_max_intensity, coords_of_COM

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

def getModifiedImage(x0,y0,x1,y1,image):
    tmp_image = image

    width, height = utility.getSize(image)

    k = (y1-y0)/(x1-x0)
    b = (y0*x1-y1*x0)/(x1-x0)

    

    point0 = (x0,y0)
    point1 =  (x1, y1)

    point0_new, point1_new = utility.getIntersections(point0, point1, image)

    draw = ImageDraw.Draw(tmp_image)

    # print(point0, point1)

    line_color = 255  
    line_width = 2  # Width of the line
    draw.line([point0_new, point1_new], fill = line_color, width = line_width)

    return tmp_image

def analyseAll(path):
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
        
        x0,y0,x1,y1, bestval = optimisation(norm_image, name)

        plotname, width = plotBepis(x0,y0,x1,y1,norm_image, name)
        

        number, _ , test_for_d_o = plotname.partition("_")
        
        
        if (test_for_d_o == "d"):
            width_data_d.append(width)
            new_names.append(number)
        elif (test_for_d_o == "o"):
            width_data_o.append(width)
        image.close()
        norm_image.close()

        print("------------------")
    
    # integral = getIntegral(x0,y0,x1,y1,image)
    if (len(new_names)!=len(width_data_d) or len(new_names)!=len(width_data_o) ):
        print("error with files")
    
    utility.printReportToCSV(new_names, width_data_d, width_data_o)


def analyseFile(path, name):
    image = img.open(os.path.join(path, name))
    
    norm_image = utility.normalizeImage(image, name)
    x0,y0,x1,y1, bestval = optimisation(norm_image)

    plotname, width = plotBepis(x0,y0,x1,y1,norm_image,name)
        
    print(plotname,",",width)

