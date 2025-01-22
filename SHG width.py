from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.interpolate import make_interp_spline,interp1d

path = 'C:/Users/123/Pictures'

names = ['b880.tif', 'D48.tif','D747.tif']

images = []
images_fixed = []
for name in names:
    image = Image.open(os.path.join(path,name)).convert('L')
    images.append(image)

coms = []

def getCOM(arr):
    tmp_arr = arr.copy()
    tmp_arr[tmp_arr < 20] = 0

    x = np.sum(np.sum(tmp_arr, axis=0) * np.arange(width)) / np.sum(tmp_arr)
    y = np.sum(np.sum(tmp_arr, axis=1) * np.arange(height)) / np.sum(tmp_arr)

    return(int(x),int(y))

delta = 200

plt.figure(figsize=(10, 5))

num_points = 20  # Number of points to sample along the line

intensities_full = []
for image in images:

    width, height = image.size

    arr = np.asarray(image)
    arr = arr.astype('float')

    arr[arr>240]= 0

    minval = arr.min()
    maxval = arr.max()

    if minval != maxval:
        arr -= (minval)
        arr *= (255.0/(maxval-minval))

    com = getCOM(arr)
    coms.append(com)

    arr[arr<10] = 0

    images_fixed.append(Image.fromarray(arr.astype('uint8'), 'L'))

    x1,y1 = (com[0]-delta, com[1])
    x2, y2 = (com[0]+delta, com[1])

    x_values = np.linspace(x1, x2, num_points)
    y_values = np.linspace(y1, y2, num_points)

    # Get the intensity values at these points
    intensities = []
    x_arr =[]
    y_arr = []
    for x, y in zip(x_values, y_values):
        # Ensure we are within the image bounds
        if 0 <= int(x) < arr.shape[1] and 0 <= int(y) < arr.shape[0]:
            intensities.append(arr[int(y), int(x)])
        else:
            intensities.append(0)  # Out of bounds, set intensity to 0

    x_indices = np.arange(num_points)
    interpolator = interp1d(x_indices, intensities, kind='cubic')  # Use cubic interpolation
    x_smooth = np.linspace(0, num_points - 1, 500)  # More points for a smooth curve
    intensities_smooth = interpolator(x_smooth)
                                      
    intensities_full.append(intensities_smooth)


for i in range(len(names)):

    plt.plot(intensities_full[i], label = names[i])


plt.title('Распределение интенсивности в горизонтальной плоскости (SHG 1, 808+808 -> 404)')
plt.xlabel('Условная координата')
plt.ylabel('Яркость')
plt.legend()
plt.grid()
plt.show()


