
import numpy as np
from PIL import Image

import cv2

from constants import * 


class GenericCamera():
    def __init__(self, camera_index = 0):
        try:
            self.camera_index = camera_index
            self.cam = cv2.VideoCapture(camera_index) 
            self.width, self.height = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        except: 
            print('Error during Generic Camera Initialisation')

    def setExposure(self, exposure_time_ms):
        print('Generic cameras usually don''t have ability to contol their exposure')
    
    def cameraFeed(self, master_app):
        while True:
            try:
                ret, frame = self.cam.read() 
                if (ret):
                    arr_img = cv2.cvtColor(frame, cv2.cv.COLOR_RGB2GRAY) 
                    master_app.camera_feed_image = Image.fromarray(arr_img) 
                else:
                    print('still not ready')
            except:
                print('Well, still no luck in Camera.cameraFeed(args), what a big surprise!')
            finally:
                try:
                    self.cam.release()
                    cv2.destroyAllWindows()
                except:
                    print('I think you know where the problem is, anyways, check out cameraFeed on exit')

    def waitForFrame(self):
        ret = False
        try:
            ret = self.cam.read()[0]
        except:
            pass
        return ret

def isCameraConnected(index):
        ret = False
        try:
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                ret = True
            cap.release()
        except:
            pass
        return ret




