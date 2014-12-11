from . import cameraActor.Camera

camera = Camera.start()

def take_picture(params):
    picture = camera.ask({'msg': 'TAKE_PICTURE', 'params': params}) 
    camera.tell({'msg': 'CONTINUE_RECORDING'})
    return picture

def start_recording(params):    
    camera.tell({'msg': 'START_RECORDING', 'params': params})
    
def stop_recording():
    camera.tell({'msg': 'STOP_RECORDING'})    