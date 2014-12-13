from cameraActor import Camera
import pykka
import signal
import sys

camera = Camera.start()

def take_picture(params):
    picture = camera.ask({'msg': 'TAKE_PICTURE', 'params': params}) 
    camera.tell({'msg': 'CONTINUE_RECORDING'})
    return picture

def start_recording(params):    
    camera.tell({'msg': 'START_RECORDING', 'params': params})
    
def stop_recording():
    camera.tell({'msg': 'STOP_RECORDING'})
    
def sigterm_handler(_signo, _stack_frame):
    
    reg = pykka.ActorRegistry()
    for act in reg.get_all():
        act.stop(block=True)
 
    sys.exit(0)
 
signal.signal(signal.SIGINT, sigterm_handler)
signal.signal(signal.SIGTERM, sigterm_handler)