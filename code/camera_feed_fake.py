import time

class FakeCamera():
    def __init__(self):
        self.frame_is_ready = False

    def setExposure(self, exposure_time_ms):
        print('Silly you, fake cameras usually don''t have ability to contol their exposure')
    
    def cameraFeed(self, master_app):
        
        self.frame_is_ready =True

        time.sleep(0.05)


    def waitForFrame(self):

        return True

    def getExposureFrac(self):
        return 1
    
    def __del__(self):
        pass
    
    def releaseCamera(self):
        print('Fake camera is "closing"')
        pass
def isCameraConnected():
    return True





