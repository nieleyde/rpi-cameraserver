import pykka
import signal
import logging
import time
import io
import picamera
import sys
import os
from subprocess import Popen, PIPE


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

logging.basicConfig(level=logging.DEBUG)
class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   """
   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''
 
   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())
 
logging.basicConfig(
   level=logging.DEBUG,
   format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
   filename="out.log",
   filemode='a'
)

class Camera(pykka.ThreadingActor):
    
    logger = None
    is_recording = False
    
    process_psips = None
    process_ffmpeg = None
    
    picamera = None
    camera = None
    
    
    def on_start(self):
        self.logger = logging.getLogger('cameraserver.actor')

        
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.debug('rpi-cameraserver: starting camera actor')
        

        self.picamera = picamera.PiCamera()
        self.camera = self.picamera.__enter__()
    
    def on_stop(self):
        self.picamera.__exit__(sys.exc_info())
        
    
    def on_receive(self, envelope):
        msg = envelope.get('msg')
        
        if(msg == 'TAKE_PICTURE'):
            self.logger.info('rpi-cameraserver: taking a picture')
            
            params = envelope.get('params')
            return self.take_picture(params)
            
        if(msg == 'START_RECORDING'):
            self.logger.info('rpi-cameraserver: starting recording')
            params = envelope.get('params')
            self.start_recording(True, params)
            
        if(msg == 'CONTINUE_RECORDING'):
            self.logger.info('rpi-cameraserver: continuing recording %r' % self.is_recording)
            self.start_recording(False)
            
        if(msg == 'STOP_RECORDING'):
            self.logger.info('rpi-cameraserver: stopping recording')
            self.stop_recording()
    
    
    def start_recording(self, init, params = None):
        if(init and not self.is_recording):
            self.is_recording = True
                        
            self.camera.resolution = (int(params.get('width', 1280)), int(params.get('height', 720)))
            self.camera.framerate = int(params.get('framerate', 5))
            self.camera.rotation = int(params.get('rotation', 180))
            
            # ensure that we have a named pipe
            if(not os.path.exists("stream.h264")):
                os.mkfifo("stream.h264")
            
            # start psips process to ensure we have SPS and PPS NALs in our h264 segments
            # psips will pipe its contents to a linux named pipe which is picked up by ffmpeg
            self.process_psips = Popen(["psips"], 
                    stdin=PIPE,
                    stdout=open('stream.h264', 'w'), 
                    stderr=StreamToLogger(logging.getLogger('psips'), logging.ERROR))
            
            # pass h264 bits from pipicamera to psips stdin
            self.camera.start_recording(psips.stdin, format='h264', bitrate=2000, quality=23)
            
            # start ffmpeg process
            self.start_ffmpeg()

            # camera.start_recording
        
        while(self.is_recording and self.actor_inbox.empty()):
            self.logger.info('rpi-cameraserver: recording')
            self.camera.wait_recording(0.5)
            
    def start_ffmpeg(self):
        # let it buffer some video before we start ffmpeg
        time.sleep(2)
        
        self.process_ffmpeg = Popen(["ffmpeg",
            "-y",
            "-i", "stream.h264",
            "-c:v", "copy", # pass the video stream through without codecing
            "-f", "segment",
            "-hls_time", "5",
            "-hls_list_size", "20",
            "-hls_wrap", "20", # restart on index 0 after 20 segments to save disk space
            "-segment_format", "mpegts",
            "-segment_list", "stream/playlist.m3u8",
            "-segment_list_flags", "live",
            "stream/%08d.ts"
            ], stderr=StreamToLogger(logging.getLogger('ffmpeg'), logging.ERROR)
             , stdout=StreamToLogger(logging.getLogger('ffmpeg'), logging.INFO))
    
    def stop_recording(self):
        self.is_recording = False
        if(camera.recording):
            self.camera.stop_recording()
            self.process_psips.terminate()
            self.process_ffmpeg.terminate()
            return "stopped recording"
        return "was already stopped"         

    
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
        
