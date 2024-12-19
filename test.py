import pylablib.devices.uc480 as pll
import time
import threading

from tkinter import *
from PIL import Image, ImageTk 
  
cam = pll.uc480.UC480Camera(backend = "uc480")
cam.open()
cam.set_pixel_rate(7e6)
cam.set_frame_period(0.005)
cam.set_frameskip_behavior('skip')
cam.set_exposure(0.003)

cam.start_acquisition()
# cam.set_frame_period()
  
# Create a GUI app 
app = Tk() 
  
def esc(event):
    cam.close()
    app.quit(event)
# Bind the app with Escape keyboard to 
# quit app whenever pressed 
app.bind('<Escape>', esc) 
  
# Create a label and display it on app 
label_widget = Label(app, ) 
label_widget.pack() 

  
# Create a function to open camera and 
# display it in the label_widget on app 

def cameraWorker():
    while(True):
        # arr_img = cam.snap()
        try:
            if(cam.wait_for_frame()):
                arr_img = cam.read_newest_image()

                img = Image.fromarray(arr_img) 
                # Convert captured image to photoimage 
                photo_image = ImageTk.PhotoImage(image=img) 

                # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                label_widget.configure(image=photo_image) 
                label_widget.photo_image = photo_image 
            else:
                print('still not ready')
        except:
            print('still not ready')

  
def open_camera(): 
    threading.Thread(target=cameraWorker, args=(), daemon=True).start()
    
  
  
# Create a button to open the camera in GUI app 
button1 = Button(app, text="Open Camera", command=open_camera) 
button1.pack() 
  
# Create an infinite loop for displaying app on screen 
app.mainloop() 

# cam = pll.uc480.UC480Camera()


