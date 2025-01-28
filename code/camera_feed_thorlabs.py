
from PIL import Image
import pylablib.devices.uc480 as pll
import time
import numpy as np
from constants import * 

import logging

class ThorCamera():
    def __init__(self):
        self.frame_is_ready = False
        try:
            self.cam = pll.uc480.UC480Camera(backend = "uc480")
            self.cam.open()
            self.cam.set_frameskip_behavior('skip')
            
            self.cam.set_pixel_rate(7e6)
            self.cam.set_frame_period(0.005)
            self.cam.set_exposure(0.003)

            self.cam.start_acquisition()
            self.counter = 0

        except Exception as e:
            logging.error('Error occured during ThorCam initialisation;', e)
            print('Error occured during ThorCam initialisation')
    
    def setExposure(self, exposure_time_ms):
        try:
            self.cam.set_exposure(min(exposure_time_ms, MAX_EXPOSURE_MS)/1000)
        except Exception as e:
            logging('Error during exposure set;', e)
            print('Error during exposure set')
    
    def cameraFeed(self, master_app):
        try:
            while (not self.cam.wait_for_frame()):
                time.sleep(0.05)

            arr_img = np.array(self.cam.read_newest_image())

            master_app.master.camera_feed_image = Image.fromarray(arr_img.astype('uint8'),'L')

            self.frame_is_ready =True
            self.counter+=1

            time.sleep(0.05)
        except Exception as e:
            logging.error('I fucking hate working without physical camera attached to my dying laptop \nIf this error occured on stable version of mjolnir (stable? Heh, nevermind), please check out ThorCamera.cameraFeed \nOf course I have no ideas of what had I done to cause this shitshow in the first place')
            print('I fucking hate working without physical camera attached to my dying laptop')
            print('If this error occured on stable version of mjolnir (stable? Heh, nevermind), please check out ThorCamera.cameraFeed')
            print('Of course I have no ideas of what had I done to cause this shitshow in the first place')
            # except:
            #     print('Well, still no luck in Camera.cameraFeed(args), what a big surprise!')

    def waitForFrame(self):
        ret = self.frame_is_ready
        self.frame_is_ready = False
        return ret

    def getExposureFrac(self):
        exposure_ms = self.cam.get_exposure()/1000
        return exposure_ms/MAX_EXPOSURE_MS

    def __del__(self):
        self.cam.stop_acquisition()
        self.cam.close()
    
def isCameraConnected(index = 0):
    instruments = 0 
    try:
        instruments = pll.uc480.get_cameras_number()
    except:
        return False
    
    if (instruments == 0):
        return False
    else:
        return True


