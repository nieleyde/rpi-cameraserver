#!/usr/bin/env python
from flask import Flask, request, Response
from flask import send_file, send_from_directory

import io
from still import capture

app = Flask(__name__)

from . import cameraManager


@app.route("/")
def hello():
    return "rpi-cameraserver!"

@app.route("/still")
def still():
    return Response(cameraManager.take_picture(request.args), mimetype='image/jpeg')

@app.route("/startstream")
def start_stream():
    cameraManager.start_recording()

@app.route("/stopstream")
def stop_stream():
    cameraManager.stop_recording()

@app.route("/stream/<path:filename>")
def serve_stream_data(filename):
    return send_from_directory('stream', filename)

app.debug = True
app.run(host='0.0.0.0')
