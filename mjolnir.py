
# from camera_feed import cameraHandler

import image_processing as ip 
import utility
import matplotlib.pyplot as plt
import numpy as np

from PIL import Image
import os






def main():
    # cameraHandler()




    path = "D:\Photonics\МУР 13.12"
    names = ["90_62_d.tif"]  

    # image = Image.open(os.path.join(path, name)).convert('L')

     

    
    # image_data = ip.ImageData(image,name)

    for name in names:
        ip.analyseFile(path,name)  
    
    # ip.analyseAll(path)
    # ip.analyseFile(path,name)
        
        



if __name__ == "__main__":
    main()