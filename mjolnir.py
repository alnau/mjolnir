
# from camera_feed import cameraHandler

import image_processing as ip 
import utility
import matplotlib.pyplot as plt
import numpy as np

from app import App
import utility 

import csv

from PIL import Image

import os
import logging
import sys
import traceback


utility.initializeWorkspace()
config = utility.readIni()

logging.basicConfig(
    filename=utility.resourcePath('tmp\mjolnir.log'),  
    level=logging.ERROR,        
    format='%(asctime)s - %(levelname)s - %(message)s'  
)

def log_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    print("Uncaught exception", exc_type, exc_value, exc_traceback)
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def main():
    # cameraHandler()

    # base_path = utility.resourcePath('tmp')

    # if (not os.path.exists(base_path)):
    #     os.makedirs(base_path)
    

    sys.excepthook = log_exception
    app = App(config)
    

        



if __name__ == "__main__":
    main()