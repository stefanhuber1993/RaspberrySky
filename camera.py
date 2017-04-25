#!/usr/bin/python2
import cv2
import time
import numpy as np
from collections import deque
from threading import Thread
from scipy.ndimage import measurements
from utilities import pad_to_ratio

class Camera():
    def __init__(self, channel=0):
        self.channel = channel
        self.input_deque = deque(maxlen=30 * 60 * 5)
        self.break_capture = False


    def set_channel(self, newchannel):
        print("Change from %s to %s" % (self.channel, newchannel))
        if int(newchannel) != self.channel:
            self.__del__()
            self.__init__(int(newchannel))


    def start_capture(self, verbose=False):
        self.cap = cv2.VideoCapture(self.channel)
        print("Camera warming up ...")
        time.sleep(0.5)
        if self.cap.isOpened():
            print("Successful Connection to Camera on /dev/video%s" % self.channel)
            self.c = Thread(target=self._capture, args=(self.input_deque, verbose))
            self.c.start()
            return True
        else:
            print("Failed Connection to Camera on /dev/video%s" % self.channel)
            return False


    def stop_capture(self):
        self.break_capture = True
        self.c.join()
        del self.c

    def _capture(self, deque, verbose):
        self.break_capture = False
        while not self.break_capture:
            s, img = self.cap.read()
            if s:
                if verbose:
                    print("Frame %s captured with shape %sx%s"%(len(deque), img.shape[1],img.shape[0]),)
                deque.append({
                    'time': time.time(),
                    'frame_raw': img})
        self.cap.release()

    def __del__(self):
        if hasattr(self, 'c'):
            self.stop_capture()
            print("Camera Stream Released")
        return


class StreamAnalyser():
    def __init__(self, camera):
        self.camera = camera

    def get_frame(self):
        try:
            img = self.camera.input_deque[-1]['frame_raw']
            img_jpg = self.encode_jpg(img, 95)
            return img_jpg
        except Exception as e:
            print(e)
            return ""

    def get_frame_cut(self):
        try:
            img = self.camera.input_deque[-1]['frame_raw']
            img_bw = img.mean(2)
            thr = img_bw > img_bw.mean() * 2.0
            labeled_array, num_features = measurements.label(thr)
            size = np.bincount(labeled_array.ravel())
            biggest_label = size[1:].argmax() + 1
            clump_mask = labeled_array == biggest_label

            B = np.argwhere(clump_mask)
            (ystart, xstart), (ystop, xstop) = B.min(0), B.max(0) + 1
            Atrim = img[ystart:ystop, xstart:xstop]

            if Atrim.size < 16 ** 2:
                return ""

            Atrim_aspect_corr = pad_to_ratio(Atrim, 4.0 / 3.0)
            img_jpg = self.encode_jpg(Atrim_aspect_corr, 95)

            return img_jpg
        except Exception as e:
            print(e)
            return ""

    def get_nonsense(self):
        nonsense = (np.random.rand(120, 160, 3) * 255).astype(np.uint8)
        img_jpg = self.encode_jpg(nonsense, 50)
        return img_jpg

    @staticmethod
    def encode_jpg(img, qual):
        return cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, qual])[1].tostring()