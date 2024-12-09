import numpy as np
import time
import csv
import cv2
import matplotlib.pyplot as plt

import scipy as sp
from scipy.optimize import differential_evolution

from constants import *

from PIL import Image as img





def getReport(name, h_width, left_side_mm, right_side_mm, coords_of_max_intensity, coords_of_com, angle):
    str_name = "Имя файла: " + name + "\n"
    str_date = "Дата анализа: " + time.strftime("%d.%m.%Y") + "\n"
    str_width = "Полуширина по уровню 0.135: " + str(round(h_width,2)) + " (мм) \n"
    str_angle = "Угол поворота оси: " + str(round(angle,2)) + " (град) \n"
    str_max_I = "Координаты максимума интенсивности: " + str(round(coords_of_max_intensity[0],2)) + ", " + str(round(coords_of_max_intensity[1],2)) + " (мм) \n"
    str_COM = "Координаты центра масс пучка: " + str(round(coords_of_com[0],2)) + ", " + str(round(coords_of_com[1],2)) + " (мм) \n"

    report = str_name + str_date + str_width + str_angle + str_max_I + str_COM
    print(report)
    
    return report


def bresnanLine(p1,p2, width, height):
    x1 = p1[0]
    y1 = p1[1]

    x2 = p2[0]
    y2 = p2[1]

    if (x1 == x2):
        # вертикальная линя
        xcoordinates = x1+np.zeros(height)
        ycoordinates = np.arange(height)
        return xcoordinates, ycoordinates

    elif (y1 == y2):
        #горизонтальная линия
        xcoordinates = np.arange(width)
        ycoordinates = y1+np.zeros(width)
        return xcoordinates, ycoordinates

    x,y = x1,y1
    dx = abs(x2 - x1)
    dy = abs(y2 -y1)
    gradient = dy/float(dx)

    if gradient > 1:
        dx, dy = dy, dx
        x, y = y, x
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    p = 2*dy - dx
    xcoordinates = [x]
    ycoordinates = [y]

    for k in range(2, dx + 2):
        if p > 0:
            y = y + 1 if y < y2 else y - 1
            p = p + 2 * (dy - dx)
        else:
            p = p + 2 * dy

        x = x + 1 if x < x2 else x - 1

        if (x > width or y > height):
            break
        #print(f"x = {x}, y = {y}")
        xcoordinates.append(x)
        ycoordinates.append(y)
    return xcoordinates, ycoordinates

def getSize(image):
    width, height = image.size
    return width, height

def getIntersections(point1, point2, image):

    x1, y1 = point1
    x2, y2 = point2

    image_width,image_height = getSize(image)

    # Calculate the slope (m) and y-intercept (c) of the line
    if x2 - x1 == 0:  # Vertical line
        m = np.inf
        c = x1
    else:
        m = (y2 - y1) / (x2 - x1)
        c = y1 - m * x1

    # Initialize a list to store the intersection points
    intersections = []
    intersection_counter = 0
    # Check intersection with the left border (x = 0)
    if m != 0:
        y_intersect = int(m * 0 + c)
        if 0 <= y_intersect < image_height:
            intersections.append((0, y_intersect))
            intersection_counter +=1

    # Check intersection with the right border (x = image_width)
    if m != 0:
        y_intersect = int(m * image_width + c)
        if 0 <= y_intersect < image_height:
            intersections.append((image_width-1, y_intersect))
            intersection_counter +=1
            if (intersection_counter == 2):
                return intersections

    # Check intersection with the top border (y = 0)
    if m != np.inf:
        x_intersect = int((0 - c) / m)
        if 0 <= x_intersect < image_width:
            intersections.append((x_intersect, 0))
            intersection_counter +=1
            if (intersection_counter == 2):
                return intersections

    # Check intersection with the bottom border (y = image_height)
    if m != np.inf:
        x_intersect = int((image_height - c) / m)
        if 0 <= x_intersect < image_width:
            intersections.append((x_intersect, image_height-1))


    return intersections



def normalize(arr):
    arr = arr.astype('float')
    # Do not touch the alpha channel

    minval = arr[...].min()
    maxval = arr[...].max()
    if minval != maxval:
        arr[...] -= minval
        arr[...] *= (255.0/(maxval-minval))
    return arr

def normalizeImage(image, name):
   
    print(name, "normalization had been started...")
    start = time.time()
    # TODO возникает ошибка где-то здесь. Какое-то переполнение буффера: ValueError: buffer is not large enough
    arr = np.array(image)
    

    new_img = img.fromarray(normalize(arr).astype('uint8'),'L')
    end = time.time()
    print("Well, that was too fast. Man, it took only", "{:.1f}".format(end-start),"s")
    return new_img

def thresholdImage(image, threshold):
    threshold_int = int(255*threshold)
    tmp_image = image

    image_as_np = np.asarray(tmp_image.convert('L'))
    ret,thresh_img = cv2.threshold(image_as_np,threshold_int,254,cv2.THRESH_BINARY)

    ret_image = img.fromarray(thresh_img.astype('uint8'),'L')

    return ret_image


def printReportToCSV(new_names, width_data_d, width_data_o):
    csv_name = "lastResults/" + time.strftime("%d-%m-%Y_", time.gmtime()) + "data.csv"
    with open(csv_name, 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["name", "d, mm", "o, mm"]

        
        writer.writerow(field)
        for i in range(len(new_names)):
            string = str(new_names[i]) + "," + str(width_data_d[i]) + "," + str(width_data_o[i])
            print(string)
            writer.writerow([str(new_names[i]), str(width_data_d[i]), str(width_data_o[i])])


def getIntegral(x1,y1,x2,y2,image, moment = 0):
        if (x1 == x2 and y1 == y2):
            return -1000000

        width, height = getSize(image)

        brightnessValues = []

        p1 = (x1,y1)
        p2 = (x2,y2)
        
        x_coords_index, y_coords_index = bresnanLine(p1,p2, width, height)
        

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
                deltaLineCoord = PIXEL_TO_MM*np.sqrt((x_coords_index[i]-x_coords_index[i+1])**2 + (y_coords_index[i] - y_coords_index[i+1])**2)
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
    trial_image = thresholdImage(image, 0.12)
    start = time.time()
    width,height = getSize(trial_image)
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
