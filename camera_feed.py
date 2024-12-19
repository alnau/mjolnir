
import numpy as np
import cv2 
from instrumental.drivers.cameras import uc480
import time
from PIL import Image

from constants import * 


class Camera():
    def __init__(self):
        self.cam = 0

        try:
            instruments = uc480.list_instruments()
            self.cam = uc480.UC480_Camera(instruments[0])
            self.cam.start_live_video(framerate='10Hz', timeout = '0.3s')

        except:
            print('Error during cam init')



    def setExposure(self, exposure_time_ms):
        try:
            self.cam.set_exposure_time(min(exposure_time_ms, MAX_EXPOSURE_MS))
        except:
            print('Error during exposure set')

    
    
    def cameraFeed(self, master_app):
        # camera = uc480.UC480_Camera()
        # camera.start_live_video(framerate=10)
        master_handle = master_app
        try:
            while True:
                if (self.cam.wait_for_frame()):
                    frame = self.cam.grab_image(timeout='100s', copy=True, exposure_time='3ms')
                    master_app.camera_feed_image = Image.fromarray(frame)
                    time.sleep(0.05)  # 10 Hz refresh rate
        except:
            print('Well, still no luck in Camera.cameraFeed(args), what a big surprise!')
        finally:
            try:
                self.stop_live_video()
                self.close()
            except:
                print('I think you know where the problem is, anyways, check out cameraFeed')

def isThorCameraConnected():
    instruments =[]
    try:
        instruments = uc480.list_instruments()
    except:
        return False
    
    if (len(instruments) == 0):
        return False
    else:
        return True


# class Camera(uc480.UC480_Camera):
#     # def __init__(self):
#     #     super()._initialize()
    
#     #     try:
#     #         self.start_live_video(framerate=10)
#     #         self.set_auto_exposure(enable = False)
#     #     except:
#     #         print('Error during cam init')

#     def _initialize(self):
#         super()._initialize()
    
#         try:
#             self.start_live_video(framerate=10)
#             self.set_auto_exposure(enable = False)
#         except:
#             print('Error during cam init')

#     def setExposure(self, exposure_time_ms):
#         try:
#             self.set_exposure_time(min(exposure_time_ms, MAX_EXPOSURE_MS))
#         except:
#             print('Error during exposure set')

    
    
#     def cameraFeed(self, shared_image):
#         # camera = uc480.UC480_Camera()
#         # camera.start_live_video(framerate=10)
        
#         try:
#             while True:
#                 frame = self.latest_frame()
#                 shared_image['image'] = Image.fromarray(frame)
#                 time.sleep(0.1)  # 10 Hz refresh rate
#         finally:
#             self.stop_live_video()
#             self.close()


def cameraFeed():
    instruments = uc480.list_instruments()
    cam = uc480.UC480_Camera(instruments[0])
    cam.start_live_video(framerate = "10Hz")

    while cam.is_open:
  
                    
        frame = cam.grab_image(timeout='100s', copy=True, exposure_time='3ms')
        
        frame1 = np.stack((frame,) * 3,-1) 
        frame1 = frame1.astype(np.uint8)

        gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)

        cv2.imshow('Camera', gray)

        
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cam.close()
    cv2.destroyAllWindows()

# cameraFeed()

def getImage(cam):
    frame = cam.grab_image(timeout='0.3s', copy=True, exposure_time='10ms')
        
    frame1 = np.stack((frame,) * 3,-1) 
    frame1 = frame1.astype(np.uint8)

    gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)

    return gray
    
cameraFeed()

# def initCamera():
#     # cv2.setMouseCallback('image',draw_circle)

#     instruments = uc480.list_instruments()
#     cam = uc480.UC480_Camera(instruments[0])
#     cam.start_live_video(framerate = "10Hz")

#     while cam.is_open:
        
#         image = getImage(cam)
#         cv2.imshow('Camera', image)
        
#         if cv2.waitKey(30) & 0xFF == ord('q'):
#             break

#     cam.close()
#     cv2.destroyAllWindows()

