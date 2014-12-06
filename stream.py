import os, os.path
import sys
from subprocess import Popen, PIPE

import threading
import time
import traceback

_camera = None

_thread_psips = None
_thread_ffmpeg = None

_active = True


def start_recording(camera):
    
    _camera = camera
    
    camera.resolution = (1280, 720)
    camera.framerate = 5
    camera.rotation = 180
    
    # ensure that we have a named pipe
    if(not os.path.exists("stream.h264")):
        os.mkfifo("stream.h264")
    
    # start psips process to set necessary headers in h264 segments
    # psips will pipe its contents to a linux named pipe
    psips = Popen(["psips"], stdin=PIPE, stdout="stream.h264")
    
    # pipe video recording from picamera to psips process
    camera.start_recording(psips.stdin, format='h264', bitrate=2000, quality=23)
 
    try:    
        # let it buffer some video before we start ffmpeg
        time.sleep(2)
        
        _thread_ffmpeg = threading.Thread(target=run_ffmpeg)
    
        while _active:
            camera.wait_recording(4)
            
    except KeyboardInterrupt:
        print("keyboard interrupt ...")
        camera.stop_recording()
        psips.stdin.close()
        ffmpeg.exit()
        
    except:
        print("Error: unable to start threads")
        print(traceback.format_exc())
    

def run_ffmpeg():
    ffmpeg = Popen(["ffmpeg", 
        "-y", 
        "-i", "stream.h264",
        "-c:v", "copy", # pass the video stream through without codecing
        "-f", "segment",
        "-hls_time", "5",
        "-hls_list_size", "10",
        "-segment_format", "mpegts",
        "-segment_list", "stream/playlist.m3u8",
        "-segment_list_flags", "live",
        "-segment_list_type", "m3u8",
        "stream/%08d.ts" 
    ])

# Define a function for the thread
def start(camera):

    # Create two threads as follows
    try:    
        _thread_psips = threading.Thread(target=start_recording, args=(camera))
        _thread_psips.start()
       
    except:
        print("Error: unable to start threads")
        print(traceback.format_exc())
    
    # GET /photo camera.capture('/project/foo.jpg', use_video_port=False)

    # GET /video
    
def stop():
    _active = False
    
    _camera.stop_recording()
    #stop streaming
    
    # stop ffmpeg thread
    
    # then stop camera
    
    # then stop psips
    
    
    
