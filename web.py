#!/usr/bin/env python
from flask import Flask, render_template, Response, redirect, url_for, g
# Emulated camera
from camera import Camera, StreamAnalyser
import time
import json

app = Flask(__name__)
camera = Camera(-1)
analyser = StreamAnalyser(camera)


def get_stream(frame_production_method, fps):
    def encode_as_content(jpg_str):
        if jpg_str == "":
            return ""
        else:
            return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + str(jpg_str) + b'\r\n'

    def frame_generator(frame_production_method, fps):
        while True:
            frame = frame_production_method()
            time.sleep(1.0 / fps)
            yield encode_as_content(frame)

    return Response(frame_generator(frame_production_method, fps=fps),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))


@app.route('/set_camera/<channel>', methods=['GET'])
def set_camera(channel):
    camera.set_channel(channel)
    success = camera.start_capture(verbose=False)
    return json.dumps({'success':success})


@app.route('/set_imaging_parameters/<exposure>', methods=['GET'])
def set_imaging_parameters(exposure):
    camera.set_imaging_parameters(exposure)
    return ()

@app.route('/video_feed')
def video_feed():
    return get_stream(analyser.get_frame, fps=10)


@app.route('/max_feed')
def max_feed():
    return get_stream(analyser.get_frame_cut, fps=2)

@app.route('/focus_feed')
def focus_feed():
    return get_stream(analyser.get_frame_focuspeak, fps=2)


@app.route('/test_feed')
def test_feed():
    return get_stream(analyser.get_nonsense, fps=1)

@app.route('/hist_feed')
def hist_feed():
    return get_stream(analyser.get_frame_hist, fps=10)

@app.route('/power_feed')
def power_feed():
    return get_stream(analyser.get_frame_power, fps=10)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True, use_reloader=False)
