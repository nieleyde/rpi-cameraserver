import picamera
import sys
from subprocess import Popen, PIPE

print("starting..")

with picamera.PiCamera() as camera:
    psips = Popen(["psips"], stdin=PIPE, stdout="stream/live.h264")
    camera.resolution = (1280, 720)
    camera.framerate = 5
    camera.rotation = 180
    
    camera.start_recording(psips.stdin, format='h264', bitrate=2000, quality=23)
     
    try:
        while True:
           camera.wait_recording(4)
    except KeyboardInterrupt:
        print("stopping recording ...")
        camera.stop_recording()
        psips.stdin.close()


    # GET /photo camera.capture('/project/foo.jpg', use_video_port=False)

    # GET /video

