
import numpy as np
import cv2 
from instrumental.drivers.cameras import uc480
import time
from PIL import Image

import constants as const

def setExposure(camera, exposure_time_ms):
    try:
        camera.set_exposure_time(min(exposure_time_ms, const.MAX_EXPOSURE_MS))
    except:
        print('Error during exposure set')

def initCamera():
    try:
        cam = uc480.UC480_Camera()
        cam.start_live_video(framerate=10)
        return cam
    except:
        print('Error during cam init')
        return 0
    
def cameraFeed(camera, shared_image):
    # camera = uc480.UC480_Camera()
    # camera.start_live_video(framerate=10)
    
    try:
        while True:
            frame = camera.latest_frame()
            shared_image['image'] = Image.fromarray(frame)
            time.sleep(0.1)  # 10 Hz refresh rate
    finally:
        camera.stop_live_video()
        camera.close()


# def cameraFeed():
#     instruments = uc480.list_instruments()
#     cam = uc480.UC480_Camera(instruments[0])
#     cam.start_live_video(framerate = "10Hz")

#     while cam.is_open:
     
#         frame = cam.grab_image(timeout='100s', copy=True, exposure_time='10ms')
        
#         frame1 = np.stack((frame,) * 3,-1) 
#         frame1 = frame1.astype(np.uint8)

#         gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)

#         cv2.imshow('Camera', gray)

#         events = [i for i in dir(cv2) if 'EVENT' in i]
#         if (len(events)!=0):
#             print( events )

        
#         if cv2.waitKey(30) & 0xFF == ord('q'):
#             break

#     cam.close()
#     cv2.destroyAllWindows()

def getImage(cam):
    frame = cam.grab_image(timeout='100s', copy=True, exposure_time='10ms')
        
    frame1 = np.stack((frame,) * 3,-1) 
    frame1 = frame1.astype(np.uint8)

    gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)

    return gray
    


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

