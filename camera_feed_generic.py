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
        ret, frame = self.cam.read()
        while(not ret):
            ret, frame = self.cam.read()
        arr_img = cv2.cvtColor(frame, cv2.cv.COLOR_RGB2GRAY) 
        master_app.camera_feed_image = Image.fromarray(arr_img) 


    def waitForFrame(self):
        ret = False
        try:
            ret = self.cam.read()[0]
        except:
            pass
        return ret

    def getExposureFrac(self):
        # TODO поднять ошибку или вывести в строку логов
        return 1
    
    def __del__(self):
        self.cam.release()
        cv2.destroyAllWindows()
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





