
import numpy as np
from PIL import Image

from camera_feed_generic import GenericCamera
from camera_feed_thorlabs import ThorCamera


from constants import * 


class Camera():
    def __init__(self, index = 0, type = 'thor'):
        if (type == 'thor'):
            self.cam = ThorCamera()
        else:
            self.cam = GenericCamera(index)

