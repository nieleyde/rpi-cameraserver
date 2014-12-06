#!/usr/bin/env python
from flask import Flask, request, Response

import io
import still, stream
#import picamera

app = Flask(__name__)

#with picamera.PiCamera() as camera:
    
@app.route("/")
def hello():
    return "Hello World!"

@app.route("/still")
def capturestill():
    #my_stream = io.BytesIO()
    #still.capture(camera, my_stream)
    #return Response(my_stream)
    
    return "hello still"

@app.route("/startstream")
def start_stream():
    stream.start(camera)

@app.route("/stopstream")
def stop_stream():
    stream.stop()

    
app.run()