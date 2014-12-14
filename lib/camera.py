import pykka
import signal
import logging
import time
import io
import sys
import os
from subprocess import Popen, PIPE

from lib.util import StreamToLogger 

log = logging.getLogger('cameraserver.actor')


class Camera():
    
    camera = None
    
    def __init__(self, picamera):
        self.camera = CameraActor.start(picamera)
        signal.signal(signal.SIGINT, self.sigterm_handler)
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        
    def take_picture(self, params = dict()):
        picture = self.camera.ask({'msg': 'TAKE_PICTURE', 'params': params}) 
        self.camera.tell({'msg': 'CONTINUE_RECORDING'})
        return picture

    def start_recording(self, params = dict()):    
        self.camera.tell({'msg': 'START_RECORDING', 'params': params})
        
    def stop_recording(self):
        self.camera.tell({'msg': 'STOP_RECORDING'})
    
    def stop(self):
        self.camera.stop()
        
    def sigterm_handler(self, _signo, _stack_frame):
        self.camera.stop()
        sys.exit(0)


class CameraActor(pykka.ThreadingActor):
    
    is_recording = False
    
    process_psips = None
    process_ffmpeg = None
    
    picamera = None
    camera = None
    
    
    def __init__(self, picamera):
        super(pykka.ThreadingActor, self).__init__()
        self.picamera = picamera
    
    def on_start(self):
        log.info('starting')
        self.camera = self.picamera.__enter__()

    def on_stop(self):
        log.info('stopping')
        self.stop_recording()
        self.camera.__exit__(sys.exc_info())
    
    def on_receive(self, envelope):
        msg = envelope.get('msg')
        
        if(msg == 'TAKE_PICTURE'):
            log.info('take picture')
            
            params = envelope.get('params')
            return self.take_picture(params)
            
        if(msg == 'START_RECORDING'):
            log.info('start recording')
            params = envelope.get('params')
            self.start_recording(True, params)
            
        if(msg == 'CONTINUE_RECORDING'):
            log.info('continue recording')
            self.start_recording(False)
            
        if(msg == 'STOP_RECORDING'):
            log.info('stop recording')
            self.stop_recording()
    
    
    def start_recording(self, init, params = None):
        if(init and not self.is_recording):
            self.is_recording = True
                        
            self.camera.resolution = (int(params.get('width', 1280)), 
                                      int(params.get('height', 720)))
            self.camera.framerate = int(params.get('framerate', 5))
            self.camera.rotation = int(params.get('rotation', 180))
            
            # ensure that we have a named pipe
            #if(not os.path.exists("stream.h264")):
            #    os.mkfifo("stream.h264")
            
            log.info('starting psips process')
            
            # start psips process to ensure we have SPS and PPS NALs in our h264 segments
            # psips will pipe its contents to a linux named pipe which is picked up by ffmpeg
            self.process_psips = Popen(["psips"],
                    shell=False,
                    stdin=PIPE,
                    stdout=PIPE, 
                    stderr=None)
            
            log.info('starting recording')
            
            # pass h264 bits from pipicamera to psips stdin
            self.camera.start_recording(self.process_psips.stdin, format='h264', bitrate=2000, quality=23)
            
            log.info('starting ffmpeg process')
            
            # start ffmpeg process
            self.start_ffmpeg()
            
        
        log.info(" is_recording? %r  inbox empty? %r" % (self.is_recording, self.actor_inbox.empty()))
        while(self.is_recording and self.actor_inbox.empty()):
            log.info("recording")            
            self.camera.wait_recording(0.5)
            
    def start_ffmpeg(self):
        # let it buffer some video before we start ffmpeg
        time.sleep(.5)
        
        self.process_ffmpeg = Popen(["ffmpeg",
            "-hide_banner", # disable version and build information in logging
            "-y",
            "-i", "pipe:0",
            "-c:v", "copy", # pass the video stream through without codecing
            "-f", "segment",
            "-hls_time", "5",
            "-hls_list_size", "20",
            "-hls_wrap", "20", # restart on index 0 after 20 segments to save disk space
            "-segment_format", "mpegts",
            "-segment_list", "stream/playlist.m3u8",
            "-segment_list_flags", "live",
            "stream/%08d.ts"
            ],
            stdin=self.process_psips.stdout,
            stderr=None, 
            stdout=None)
    
    def stop_recording(self):
        self.is_recording = False
        
        if(self.camera.recording):
            
            log.info('terminating ffmpeg')
            self.process_ffmpeg.terminate()
            self.process_ffmpeg.wait()
            
            log.info('stopping recording')
            self.camera.stop_recording()
            
            log.info('terminating psips')
            self.process_psips.terminate()
            self.process_psips.wait()

    def take_picture(self, params):
        
        camera = self.camera
        
        camera.rotation = params.get('rotation', 180)
        camera.resolution = (int(params.get('width', 1280)), int(params.get('height', 720)))

        camera.iso = int(params.get('iso', 0))
        camera.saturation = int(params.get('saturation', 0))
        camera.sharpness = int(params.get('sharpness', 0))
        camera.shutter_speed = int(params.get('shutter_speed', 0))
        
        camera.awb_mode = params.get('awb_mode', 'auto')
        camera.brightness = int(params.get('brightness', 50))
        camera.contrast = int(params.get('contrast', 0))
        camera.drc_strength = params.get('drc_strength', 'off')
        camera.exposure_compensation = int(params.get('exposure_compensation', 0))
        camera.exposure_mode = params.get('exposure_mode', 'auto')

        camera.meter_mode = params.get('meter_mode', 'average')

        camera.image_denoise = params.get('disable_image_denoise') == "true"
        camera.image_effect = params.get('image_effect', 'none')

        camera.hflip = params.get('hflip') == "true"
        camera.vflip = params.get('vflip') == "true"

        camera.exif_tags['IFD0.Copyright'] = 'Dag Einar Monsen <me@dag.im>'

        quality = int(params.get('quality', 90))

        # focus camera if it's not already recording
        if(not self.is_recording):
            camera.start_preview()
            time.sleep(0.2)

        stream = io.BytesIO()
        camera.capture(stream, format='jpeg', quality=quality)
        
        return stream.getvalue()
        
