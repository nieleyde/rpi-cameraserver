#!/usr/bin/env python

from flask import Flask, request, Response
from flask import send_file, send_from_directory
from picamera import PiCamera
from lib.camera import Camera
import traceback
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(name)s] %(levelname)s %(message)s')

try:
    camera = Camera(PiCamera())

    app = Flask(__name__)

    @app.route("/")
    def hello():
        return "rpi-cameraserver!"

    @app.route("/still")
    def still():
        return Response(camera.take_picture(request.args), mimetype='image/jpeg')

    @app.route("/startstream")
    def start_stream():
        camera.start_recording(request.args)
        return Response('{"message": "starting"}')

    @app.route("/stopstream")
    def stop_stream():
        camera.stop_recording()
        return Response('{"message": "stopping"}')
        

    @app.route("/stream/<path:filename>")
    def serve_stream_data(filename):
        return send_from_directory('stream', filename)

    app.run(host='0.0.0.0')
    
    
    #camera.stop()
    
except KeyboardInterrupt:
    print("stooooppp")
    raise


except:
    print("Caught it!")
    print(traceback.format_exc())
