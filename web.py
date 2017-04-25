#!/usr/bin/env python
from flask import Flask, render_template, Response, redirect, url_for, g
# Emulated camera
from camera import Camera
import time


app = Flask(__name__)
camera = Camera(-1)

@app.route('/')
def index():
    """Video streaming home page."""
    return redirect(url_for('static', filename='index.html'))
    #return render_template('index.html')

def encode_as_content(jpg_str):
    if jpg_str == "":
        return ""
    else:
        return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + str(jpg_str) + b'\r\n'


def gen(camera):
    """Video streaming generator function."""
    #time.sleep(3)
    while True:#not camera.break_capture:
        frame = camera.get_frame()
        time.sleep(0.1)
        yield encode_as_content(frame)

def gen_max(camera):
    """Video streaming generator function."""
    #time.sleep(3)
    while True:#not camera.break_capture:
        frame = camera.get_frame_cut()
        time.sleep(0.1)
        yield encode_as_content(frame)

def gen_nonsense(camera):
    """Video streaming generator function."""
    while True:#not camera.break_capture:
        frame = camera.get_nonsense()
        time.sleep(0.1)
        yield encode_as_content(frame)


@app.route('/set_camera/<channel>', methods=['GET'])
def set_camera(channel):
    """Initialise Camera"""
    global camera
    print("Test")
    camera.set_channel(channel)
    camera.start_capture(verbose=False)
    time.sleep(0.5)
    return 'OK' 


@app.route('/video_feed')
def video_feed():
    global camera
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/max_feed')
def max_feed():
    global camera
    """Video streaming route. Put this in the src attribute of an img tag."""
    #return Response(gen(Camera()),
    #                mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(gen_max(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/test_feed')
def test_feed():
    global camera
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_nonsense(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    # return ""


if __name__ == '__main__':
    #stacktracer.trace_start("trace.html", interval=5, auto=True)  # Set auto flag to always update file!
    app.run(host='0.0.0.0', debug=True, threaded=True, use_reloader=False)
    #stacktracer.trace_stop()
