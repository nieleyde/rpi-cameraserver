import picamera
import sys
from subprocess import Popen, PIPE

print("starting..")

with picamera.PiCamera() as camera:
    dashcast = Popen(["DashCast", "-logs", "dash@info", "-live", "-conf", "dashcast.conf", "-v", "pipe:", "-vf", "h264", "-vres", "1280x720", "-vfr", "10", "-mpd-refresh", "1", "-out", "dashcast"], stdin=PIPE)
    camera.resolution = (1280, 720)
    camera.framerate = 2
    camera.rotation = 180
    
    camera.start_recording(dashcast.stdin, format='h264', bitrate=2000, quality=23)
     
    try:
        while True:
           camera.wait_recording(0.2)
    except KeyboardInterrupt:
        print("stopping recording ...")
        camera.stop_recording()
        dashcast.stdin.close()


    # GET /photo camera.capture('/project/foo.jpg', use_video_port=False)

    # GET /video

