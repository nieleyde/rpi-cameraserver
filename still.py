        
import io
import time
import picamera

def capture(camera, params):
    stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        
        camera.rotation = params.get('rotation', 180)
        camera.resolution = (int(params.get('width', 1280)), int(params.get('height', 720)))

        camera.iso = int(params.get('iso', 0))
        camera.saturation = int(params.get('saturation', 0))
        camera.sharpness = int(params.get('sharpness', 0))
        camera.shutter_speed = params.get('shutter_speed', 0)
        
        camera.awb_mode = params.get('awb_mode', 'auto')
        camera.brightness = int(params.get('brightness', 50))
        camera.contrast = int(params.get('contrast', 0))
        camera.drc_strength = params.get('drc_strength', 'off')
        camera.exposure_compensation = int(params.get('exposure_compensation', 0))
        camera.exposure_mode = params.get('exposure_mode', 'auto')

        camera.meter_mode = params.get('meter_mode', 'average')

        camera.image_denoise = not bool(params.get('disable_image_denoise', False))
        camera.image_effect = params.get('image_effect', 'none')

        camera.hflip = bool(params.get('hflip', False))
        camera.vflip = bool(params.get('vflip', False))

        camera.exif_tags['IFD0.Copyright'] = 'Dag Einar Monsen <me@dag.im>'


        quality = params.get('quality', 90)

        camera.start_preview()
        time.sleep(0.2)
        camera.capture(stream, format='jpeg', quality=quality)
        return stream

