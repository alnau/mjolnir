
# from camera_feed import cameraHandler

import image_processing as ip 

import matplotlib.pyplot as plt
import numpy as np

from PIL import Image
import os






def main():
    # cameraHandler()




    path = "D:\Photonics\KGW МУР"
    name = "!18_d.tif" 

    image = Image.open(os.path.join(path, name)).convert('L')

    image_data = ip.ImageData(image,name)

    image_data.analyseImage()

    new_image = image_data.getModifiedImage()
    new_image.show()
    

        
        



if __name__ == "__main__":
    main()