        
import io
import time

def capture(camera, stream):
    camera.capture(stream, 'jpeg')