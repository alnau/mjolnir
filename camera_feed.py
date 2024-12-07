
import numpy as np
import cv2 
from instrumental.drivers.cameras import uc480


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
    


def cameraHandler():
    # cv2.setMouseCallback('image',draw_circle)

    instruments = uc480.list_instruments()
    cam = uc480.UC480_Camera(instruments[0])
    cam.start_live_video(framerate = "10Hz")

    while cam.is_open:
        
        image = getImage(cam)
        cv2.imshow('Camera', image)
        
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cam.close()
    cv2.destroyAllWindows()

