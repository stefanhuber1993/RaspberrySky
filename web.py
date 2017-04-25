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


def encode_as_content(jpg_str):
    if jpg_str == "":
        return ""
    else:
        return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + str(jpg_str) + b'\r\n'


def get_stream(frame_production_method, fps):
    def frame_generator(frame_production_method, fps):
        while True:
            frame = frame_production_method()
            time.sleep(1.0/fps)
            yield encode_as_content(frame)
    return Response(frame_generator(frame_production_method, fps=fps),
             mimetype='multipart/x-mixed-replace; boundary=frame')


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
    return get_stream(camera.get_frame, fps=20)

@app.route('/max_feed')
def max_feed():
    global camera
    return get_stream(camera.get_frame_cut, fps=20)

@app.route('/test_feed')
def test_feed():
    global camera
    return get_stream(camera.get_nonsense, fps=1)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True, use_reloader=False)
