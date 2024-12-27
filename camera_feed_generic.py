from PIL import Image
import cv2
import time

from constants import * 


class GenericCamera():
    def __init__(self, camera_index = 0):
        self.counter = 0
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
        arr_img = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) 
        # Тупой баг. Программа пыталась достучаться до image_frame.camera_feed_image, а не до  app.camera_feed_image
        # следствие тупого рефакторинга. Идиот
        # TODO ВАЖНО: НЕ ЗАБУДЬ РАСКОММЕНТИРОВАТЬ СТРОЧКУ НИЖЕ. Закомментировал эту часть для тестирования интерейса
        # master_app.master.camera_feed_image = Image.fromarray(arr_img.astype('uint8'),'L') 

        self.frame_is_ready =True

        time.sleep(0.05)


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





