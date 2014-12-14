import logging
from camera import Camera
from mock import MagicMock
import time

def test_camera_mock():
    
    try:
        camera_mock = PicameraMock()
        
        camera = Camera(camera_mock)
        camera.take_picture()
        camera.start_recording()
        
        time.sleep(15)
        
        camera.stop_recording()
        
        time.sleep(5)
        
        camera.start_recording()
        
        time.sleep(5)
        
        camera.take_picture()
        
        time.sleep(10)
        
        camera.stop_recording()
        
        time.sleep(5)
        
        camera.take_picture()
        
        time.sleep(5)
        
        
        #camera.stop()
        
    except KeyboardInterrupt:
        print("stooooppp")
        raise
    
class PicameraMock(MagicMock):
    def wait_recording(self, duration):
        time.sleep(2)
    
    def start_recording(self, outstream, format=None, bitrate = None, quality=None):
        self.recording = True
        
    def stop_recording(self):
        self.recording = False
    
test_camera_mock()