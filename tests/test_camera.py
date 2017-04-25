from unittest import TestCase
from camera import Camera
import time


class TestCamera(TestCase):
    def test_set_channel(self):
        cam = Camera(0)
        cam.set_channel(2)
        self.assertTrue(cam.channel==2, 'Camera Channel could not be changed')
        del cam

    def test_capture(self):
        cam = Camera(0)
        success = cam.start_capture(verbose=False)
        self.assertTrue(success, 'Camera could not be connected')
        time.sleep(1)
        cam.stop_capture()
        self.assertTrue(len(cam.input_deque)>0, 'Camera did not save frames')
        del cam