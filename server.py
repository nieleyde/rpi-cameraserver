#!/usr/bin/env python
from flask import Flask, request, Response
from flask import send_file

import io
from still import capture
from stream import start, stop
import picamera

app = Flask(__name__)

        
@app.route("/")
def hello():
    return "Hello World!"

@app.route("/still")
def still():
    stream = capture(None, request.args)
    return Response(stream.getvalue(), mimetype='image/jpeg')

@app.route("/startstream")
def start_stream():
    start(camera)

@app.route("/stopstream")
def stop_stream():
    stop()

app.debug = True
app.run(host='0.0.0.0')
