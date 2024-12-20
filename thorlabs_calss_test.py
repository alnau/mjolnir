
# from PIL import Image
# import pylablib.devices.uc480 as pll
# import time
# from constants import * 

# class ThorCamera():
#     def __init__(self):
#         # TODO: класс имеет метод __init__, т.е. можно переписать через наследование
#         try:
#             self.cam = pll.uc480.UC480Camera(backend = "uc480")
#             self.cam.open()
#             self.cam.set_frameskip_behavior('skip')
            
#             self.cam.set_pixel_rate(7e6)
#             self.cam.set_frame_period(0.005)
#             self.cam.set_exposure(0.003)

#             self.cam.start_acquisition()
#             self.counter = 1
#         except:
#             print('Error occured during ThorCam initialisation')
#     def setExposure(self, exposure_time_ms):
#         try:
#             self.cam.set_exposure(min(exposure_time_ms, MAX_EXPOSURE_MS)/1000)
#         except:
#             print('Error during exposure set')
    
#     def cameraFeed(self, image):
#         while True:
#             try:
#                 if(self.cam.wait_for_frame()):
#                     arr_img = self.cam.read_newest_image()

#                     image = Image.fromarray(arr_img) 
#                     if (self.counter % 50 == 0):
#                         print(' got 50 images')
#                         image.show()
#                     self.counter+=1
#                     print(self.counter)
#                     time.sleep(0.05)
                    
#             except:
#                 print('Well, still no luck in Camera.cameraFeed(args), what a big surprise!')
#             finally:
#                 try:
#                     self.cam.stop_acquisition()
#                     self.cam.close()
#                 except:
#                     print('I think you know where the problem is, anyways, check out cameraFeed on exit')

#     def waitForFrame(self):
#         ret = False
#         try:
#             ret = self.cam.wait_for_frame()
#         except:
            
#         return ret

# def isCameraConnected(index = 0):
#     instruments = 0 
#     try:
#         instruments = pll.uc480.get_cameras_number()
#     except:
#         return False
    
#     if (instruments == 0):
#         return False
#     else:
#         return True


