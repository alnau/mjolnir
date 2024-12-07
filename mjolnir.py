
from camera_feed import cameraHandler

from image_processing import ImageData

def main():
    # cameraHandler()
    path = "D:\Photonics\KGW МУР"
    name = "!18_d.tif" 

    image_data = ImageData(path,name)
    image_data.analyseFile()
    

        
        



if __name__ == "__main__":
    main()