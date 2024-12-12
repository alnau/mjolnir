# import numpy as np
# from scipy.integrate import dblquad

# def integrate_over_polar(f, x0, y0, r_min, r_max, theta_min, theta_max):
#     """
#     Integrate a function over polar coordinates centered at (x0, y0).

#     Args:
#     - f (callable): The function to integrate, which takes two arguments (x, y).
#     - x0 (float): The x-coordinate of the center of the polar coordinates.
#     - y0 (float): The y-coordinate of the center of the polar coordinates.
#     - r_min (float): The minimum radius of the polar coordinates.
#     - r_max (float): The maximum radius of the polar coordinates.
#     - theta_min (float): The minimum angle of the polar coordinates in radians.
#     - theta_max (float): The maximum angle of the polar coordinates in radians.

#     Returns:
#     - result (float): The result of the integration.
#     - error (float): An estimate of the error in the result.
#     """

#     # Define the integrand function in polar coordinates
#     def integrand(r, theta):
#         x = x0 + r*np.cos(theta)
#         y = y0 + r*np.sin(theta)
#         return f(x, y)*r

#     # Perform the integration
#     result, error = dblquad(integrand, theta_min, theta_max,
#                             lambda theta: r_min, lambda theta: r_max)

#     return result, error

# # Example usage
# def f(x, y):
#     return x**2 + y**2

# x0, y0 = 1, 2
# r_min, r_max = 0, 3
# theta_min, theta_max = 0, 2*np.pi

# result, error = integrate_over_polar(f, x0, y0, r_min, r_max, theta_min, theta_max)
# print("Result:", result)
# print("Error:", error)

import numpy as np
import time
from scipy.interpolate import griddata
from PIL import Image
import os

def interpolate_brightness(image, coordinates):
    """
    Interpolate the brightness of a grayscale image at floating-point coordinates.

    Args:
    - image (numpy.ndarray): A 2D grayscale image.
    - coordinates (list or numpy.ndarray): A list of (x, y) floating-point coordinates.

    Returns:
    - brightness (list or numpy.ndarray): The interpolated brightness at each coordinate.

    Raises:
    - ValueError: If the image is not a 2D grayscale image.
    - ValueError: If the coordinates are not a list or numpy.ndarray of (x, y) values.
    """

    # Check if the image is a 2D grayscale image
    if len(image.shape) != 2:
        raise ValueError("Image must be a 2D grayscale image")

    # Check if the coordinates are a list or numpy.ndarray of (x, y) values
    if not isinstance(coordinates, (list, np.ndarray)):
        raise ValueError("Coordinates must be a list or numpy.ndarray of (x, y) values")

    # Convert the coordinates to a numpy array
    coordinates = np.array(coordinates)

    # Check if the coordinates have the correct shape
    if len(coordinates.shape) != 2 or coordinates.shape[1] != 2:
        raise ValueError("Coordinates must be a list or numpy.ndarray of (x, y) values")

    # Create a grid of integer coordinates for the image
    x = np.arange(image.shape[1])
    y = np.arange(image.shape[0])
    grid_x, grid_y = np.meshgrid(x, y)

    # Flatten the grid coordinates
    grid_coords = np.column_stack((grid_x.flatten(), grid_y.flatten()))

    # Flatten the image data
    image_data = image.flatten()

    # Interpolate the brightness at the floating-point coordinates
    brightness = griddata(grid_coords, image_data, coordinates, method='linear')

    return brightness

def interpolateFknHard(image_data, x,y):
    x1 = int(np.floor(x))
    y1 = int(np.floor(y))
    x2 = int(np.ceil(x))
    y2 = int(np.ceil(y))

    x_inter1 = (x2-x)/(x2-x1)*image_data[y1][x1] + (x-x1)/(x2-x1)*image_data[y1][x2]
    x_inter2 = (x2-x)/(x2-x1)*image_data[y2][x1] + (x-x1)/(x2-x1)*image_data[y2][x2]
    y_inter = (y2-y)/(y2-y1)*x_inter1 + (y-y1)/(y2-y1)*x_inter2

    return y_inter


x,y = 120.1, 120.1

path = "D:\Photonics\KGW МУР"
name = "!18_d_crop.tif" 

image = Image.open(os.path.join(path, name)).convert('L')

image_data = np.array(image)

coordinates = np.array([[x,y]])
start = time.time()
brightness = interpolate_brightness(image_data, coordinates)
end = time.time()
brightness2 = interpolateFknHard(image_data, x,y)
end2 = time.time()

print( brightness,  brightness2, image.getpixel((120,120)))