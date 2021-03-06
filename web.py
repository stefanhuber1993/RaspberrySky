#!/usr/bin/env python
from flask import Flask, render_template, Response, redirect, url_for, g
# Emulated camera
from camera import Camera
from analyser import StreamAnalyser
import time
import json

app = Flask(__name__)
camera = Camera(0)
analyser = StreamAnalyser(camera)


def get_stream(frame_production_method, fps):
    def encode_as_content(jpg_str):
        if jpg_str == "":
            return ""
        elif len(jpg_str)<200:
            return jpg_str
        else:
            return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytes(jpg_str) + b'\r\n'

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
    return json.dumps({'success': success})


@app.route('/stop_camera', methods=['GET'])
def stop_camera():
    camera.stop_capture()
    return json.dumps({'success': True})


@app.route('/set_imaging_parameters/<exposure>', methods=['GET'])
def set_imaging_parameters(exposure):
    camera.set_imaging_parameters(exposure)
    return json.dumps({'success': True})


@app.route('/video_feed')
def video_feed():
    return get_stream(analyser.get_frame, fps=20)


@app.route('/max_feed')
def max_feed():
    return get_stream(analyser.get_frame_cut, fps=5)


@app.route('/focus_feed')
def focus_feed():
    return get_stream(analyser.get_frame_focuspeak, fps=20)


@app.route('/test_feed')
def test_feed():
    return get_stream(analyser.get_nonsense, fps=1)


@app.route('/hist_feed')
def hist_feed():
    return get_stream(analyser.get_frame_hist, fps=10)


@app.route('/power_feed')
def power_feed():
    return get_stream(analyser.get_frame_power, fps=3)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, threaded=True, use_reloader=False)
