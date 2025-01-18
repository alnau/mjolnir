
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


def test():
    print(1/0)

def main():
    # cameraHandler()
    sys.excepthook = log_exception

    utility.initializeWorkspace()
    config = utility.readIni()
    # test()
    # path = "D:\Photonics\\8pcs ВОМЗ"
    # names = ["90_62_d.tif"]  
    app = App(config)
    
    # ip.analyseAll(path)
    # ip.analyseFile(path,name)
        
        



if __name__ == "__main__":
    main()