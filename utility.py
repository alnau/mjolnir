import numpy as np
import time
import csv
import cv2
import matplotlib.pyplot as plt
import xlsxwriter as xlsx
import scipy as sp
from scipy.optimize import differential_evolution
from scipy.interpolate import griddata
from scipy.integrate import dblquad
from scipy import integrate 
from PIL import Image as img

from constants import *



def getReport(name, radius, h_width, left_side_mm, right_side_mm, coords_of_max_intensity, coords_of_com, angle):
    str_name = "Имя файла: " + name + "\n"
    str_date = "Дата анализа: " + time.strftime("%d.%m.%Y") + "\n"
    str_width = "Диаметр 86.5% от интегральной энергии: " + str(round(2*radius,2)) + " (мм) \n"
    str_angle = "Угол поворота оси: " + str(round(angle,2)) + " (град) \n"
    str_max_I = "Координаты максимума интенсивности: " + str(round(coords_of_max_intensity[0],2)) + ", " + str(round(coords_of_max_intensity[1],2)) + " (мм) \n"
    str_COM = "Координаты центра масс пучка: " + str(round(coords_of_com[0],2)) + ", " + str(round(coords_of_com[1],2)) + " (мм) \n"

    report = str_name + str_date + str_width + str_angle + str_max_I + str_COM
    print(report)
    
    return report

    
def getCircleBound(point, r):
    return (point[0]-r,point[1]-r, point[0]+r, point[1]+r)


def bresnanLine(p1, p2, width, height):
    x1, y1 = p1
    x2, y2 = p2

    # На всякий пожарный
    if not (0 <= x1 < width and 0 <= y1 < height and 0 <= x2 < width and 0 <= y2 < height):
        raise ValueError("Coordinates are out of bounds.")

    xcoordinates = []
    ycoordinates = []

    # вертикаль
    if x1 == x2:
        y_range = np.arange(min(y1, y2), max(y1, y2) + 1)
        xcoordinates = [x1] * len(y_range)
        ycoordinates = list(y_range)
        return xcoordinates, ycoordinates

    # горизонталь
    elif y1 == y2:
        x_range = np.arange(min(x1, x2), max(x1, x2) + 1)
        ycoordinates = [y1] * len(x_range)
        xcoordinates = list(x_range)
        return xcoordinates, ycoordinates

    # Общий случай
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    if dy > dx:
        dx, dy = dy, dx
        x1, y1 = y1, x1
        x2, y2 = y2, x2
        sx, sy = sy, sx

    err = dx / 2.0
    while x1 != x2:
        if 0 <= x1 < width and 0 <= y1 < height:
            xcoordinates.append(x1)
            ycoordinates.append(y1)

        err -= dy
        if err < 0:
            y1 += sy
            err += dx
        x1 += sx

    # конечные точки
    if 0 <= x2 < width and 0 <= y2 < height:
        xcoordinates.append(x2)
        ycoordinates.append(y2)

    return xcoordinates, ycoordinates


def getSize(image):
    width, height = image.size
    return width, height

def getIntersections(point1, point2, image):

    x1, y1 = point1
    x2, y2 = point2

    image_width,image_height = getSize(image)

    if x2 - x1 == 0:  # Вертикаль:
        m = np.inf
        c = x1
    else:
        m = (y2 - y1) / (x2 - x1)
        c = y1 - m * x1

    intersections = []
    intersection_counter = 0
    # Левое пересечение (x = 0)
    if m != 0:
        y_intersect = int(m * 0 + c)
        if 0 <= y_intersect < image_height:
            intersections.append((0, y_intersect))
            intersection_counter +=1

    # правое пересечение (x = image_width)
    if m != 0:
        y_intersect = int(m * image_width + c)
        if 0 <= y_intersect < image_height:
            intersections.append((image_width-1, y_intersect))
            intersection_counter +=1
            if (intersection_counter == 2):
                return intersections

    # ... верх (y = 0)
    if m != np.inf:
        x_intersect = int((0 - c) / m)
        if 0 <= x_intersect < image_width:
            intersections.append((x_intersect, 0))
            intersection_counter +=1
            if (intersection_counter == 2):
                return intersections

    # ... и низ (y = image_height)
    if m != np.inf:
        x_intersect = int((image_height - c) / m)
        if 0 <= x_intersect < image_width:
            intersections.append((x_intersect, image_height-1))


    return intersections



def normalize(arr, threshold = 5):
    arr = arr.astype('float')

    minval = arr.min()
    maxval = arr.max()
    if minval != maxval:
        arr -= (minval)
        arr *= (255.0/(maxval-minval))

    return arr

def normalizeImage(image):
    arr = np.array(image)
    new_img = img.fromarray(normalize(arr).astype('uint8'),'L')

    return new_img


def getCOM(image):

    width, height = getSize(image)
    
    arr = np.array(image.convert('L'))
    arr = arr.astype('float')

    minval = arr.min()
    maxval = arr.max()
    if minval != maxval:
        arr -= (minval)
        arr *= (255.0/(maxval-minval))
    
    arr[arr < CUTOFF_THRESHOLD] = 0


    x = np.sum(np.sum(arr, axis=0) * np.arange(width)) / np.sum(arr)
    y = np.sum(np.sum(arr, axis=1) * np.arange(height)) / np.sum(arr)
    com = (int(x),int(y))
    return com



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

def fillTitleLine(worksheet_handle, r_control):
    first_line = ['№', 'диаметр d (мм)', 'диаметр o, (мм)','', 'контрольный радиус (мм)',r_control]
    counter = 0
    for cols in first_line: 
        worksheet_handle.write(0,counter, cols)
        counter+=1

def printReportToXLSX(names, r_d, r_o, r_ref = 0.337):
    xlsx_name = "lastResults/" + time.strftime("%d-%m-%Y_", time.gmtime()) + "data.xlsx"
    workbook = xlsx.Workbook(xlsx_name)
    worksheet = workbook.add_worksheet()

    fillTitleLine(worksheet, r_ref)

    index = 0
    for name in names:
        worksheet.write(index+1,0,name)
        worksheet.write(index+1, 1, float(r_d[index]))
        worksheet.write(index+1, 2, float(r_o[index]))
        index+=1

    workbook.close()
    


# возвращает (width, height)
def getBrightness(p1, p2, image):
    tmp_image = image.copy()
    tmp_image.convert('L')
    width, height = getSize(image)

    x_coords_index, y_coords_index = bresnanLine(p1,p2, width, height)
    brightness_values =[]
    length = len(x_coords_index)-1
    for i in range(length):
        brightness = tmp_image.getpixel((x_coords_index[i]-1, y_coords_index[i]-1))
        brightness_values.append(brightness)

    coords = []
    coords.append(0)
  
    conversion_factor = PIXEL_TO_MM*1280/width
    len_of_line = 0
    for i in range(length-1):
        dl = conversion_factor*np.sqrt((x_coords_index[i] - x_coords_index[i+1])**2 + (y_coords_index[i] - y_coords_index[i+1])**2)
        coords.append(len_of_line)
        len_of_line+=dl

    return coords, brightness_values



def getIntegral(x1,y1,x2,y2,image, moment = 0):
        if (x1 == x2 and y1 == y2):
            return -1000000

        width, height = getSize(image)

        brightnessValues = []

        p1 = (x1,y1)
        p2 = (x2,y2)
        
        x_coords_index, y_coords_index = bresnanLine(p1,p2, width, height)
        
        if (len(x_coords_index) < 10):
            return -100000
        
        x_coords_index.pop()
        y_coords_index.pop()

        length = len(x_coords_index)

        for i in range(length):
            try:
                brightness  = image.getpixel((x_coords_index[i] - 1, y_coords_index[i] - 1))
        
                # brightness = pixel[0]
                brightnessValues.append(brightness)
            except:
                print("error in getIntegral, possibly out of bounds")
                print(length)

        integral = 0
        try:
            np_x_coords_index = np.array(x_coords_index)
            np_y_coords_index = np.array(y_coords_index)
            np_brightness = np.array(brightnessValues)

            distances = np.sqrt(np.diff(np_x_coords_index)**2 + np.diff(np_y_coords_index)**2)  
            line_coordinates = np.insert(np.cumsum(distances), 0, 0)  

            integral = PIXEL_TO_MM*np.trapz(np_brightness, line_coordinates)
        except:
            print(len(np_x_coords_index), len(np_brightness))

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
    arr_image = np.array(image)
    arr_image[arr_image<5] = 0
    trial_image = img.fromarray(arr_image.astype('uint8'),'L')

    start = time.time()
    width,height = getSize(trial_image)
    bounds = [[1, width-1], [1,height-1], [1, width-1], [1,height-1]]
    result = differential_evolution(lambda args: funcToOptimize(args, trial_image, RMS=False), bounds)
    x0_initial, y0_initial, x1_initial, y1_initial = map(int, result.x)
    end = time.time()
  
    print("gotcha. By the way, it took", "{:.1f}".format(end-start),"s")
    return x0_initial, y0_initial, x1_initial, y1_initial



def interpolateFknHard(image_data, x,y):
    # TODO: не уверен, что это вообще нужно
    if len(image_data.shape) != 2:
        raise ValueError("Image must be a 2D grayscale image")

    height, width = image_data.shape

    x0 = int(np.floor(x))
    x1 = int(np.ceil(x))
    y0 = int(np.floor(y))
    y1 = int(np.ceil(y))

    x0 = max(0, min(x0, width - 1))
    x1 = max(0, min(x1, width - 1))
    y0 = max(0, min(y0, height - 1))
    y1 = max(0, min(y1, height - 1))

    wx = x - x0
    wy = y - y0

    top_left = image_data[y0, x0]
    top_right = image_data[y0, x1]
    bottom_left = image_data[y1, x0]
    bottom_right = image_data[y1, x1]

    top = (1 - wx) * top_left + wx * top_right
    bottom = (1 - wx) * bottom_left + wx * bottom_right
    brightness = (1 - wy) * top + wy * bottom

    return brightness


def integrateOverPolar(image, x0, y0, r_max, r_min = 0, theta_min = 0, theta_max = 2*np.pi):
    arr_image = np.array(image)
    arr_image[arr_image < CUTOFF_THRESHOLD] = 0
    
    # TODO: в очереди на удаление
    if len(arr_image.shape) != 2:
        raise ValueError("Image must be a 2D grayscale image")

    def integrand(r, theta):
        x = x0 + r*np.cos(theta)
        y = y0 + r*np.sin(theta)

        result = interpolateFknHard(arr_image, x, y)*r 

        return result 
    
    r_limits = (r_min, r_max)
    theta_limits = (theta_min, theta_max)   
    options = {'limit': 200, 'epsabs': 0.1, 'epsrel': 0.1}

    result, error = integrate.nquad(integrand, [r_limits, theta_limits], opts=options)

    return result, error

def sumOverPixels(image_data,r):
    I_in = 0
    I_sum = 0

    com = (image_data.coords_of_com[0]/PIXEL_TO_MM, image_data.coords_of_com[1]/PIXEL_TO_MM)

    for ix in range(image_data.width):
        for iy in range(image_data.height):
            if ((com[0]-ix)**2+(com[1] - iy)**2 < image_data.getRMax(com)**2):
                brightness = image_data.norm_image.getpixel((ix,iy))
                I_sum+=brightness
                if ((com[0]-ix)**2+(com[1] - iy)**2 < r**2):
                    I_in+=brightness
    return (I_in/I_sum)
