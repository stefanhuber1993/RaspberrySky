#!/usr/bin/python2
import cv2
import time
import numpy as np
from collections import deque
from threading import Thread
from scipy.ndimage import measurements
from utilities import pad_to_ratio, azimuthalAverage
from subprocess import call
from scipy import fftpack

class Camera():
    def __init__(self, channel=0):
        self.channel = channel
        self.input_deque = deque(maxlen=30 * 60 * 5)
        self.break_capture = False
        self.c = None


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
        self.c = None

    def set_imaging_parameters(self, exposure):
        base_command = ['v4l2-ctl', '--device', '/dev/video%s'%self.channel, '--set-ctrl']
        call(base_command + ['gain_automatic=0'])
        call(base_command + ['exposure=%s'%exposure])

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
        if self.c is not None:
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

    def get_frame_hist(self):
        try:
            img = self.camera.input_deque[-1]['frame_raw'].mean(2).astype(np.uint8)
            img_flat = img.flatten()
            bins = np.bincount(img_flat, minlength=256).astype(float)
            bins /= bins.max()
            bins ** 0.25
            height = float(128+64-1)
            bins *= height
            bins = bins.astype(np.int)
            histogram = np.zeros((128+64, 256), dtype=np.uint8)
            histogram[int(height)-bins, np.arange(256)] = 255
            img_jpg = self.encode_jpg(histogram, 60)
            return img_jpg
        except Exception as e:
            print(e)
            return ""

    def get_frame_power(self):
        try:
            img = self.camera.input_deque[-1]['frame_raw'].mean(2).astype(np.uint8)
            F1 = fftpack.fft2(img)
            F2 = fftpack.fftshift(F1)
            psd2D = np.log(np.abs(F2) ** 2)
            psd1D = azimuthalAverage(psd2D).astype(float)
            psd1D /= np.percentile(psd1D, 100)
            psd1D = np.clip(psd1D, 0,1)
            #psd1D ** 0.01
            height = int(len(psd1D)*0.75-1)
            psd1D *= float(height)
            psd1D = psd1D.astype(np.int)
            histogram = np.zeros((height+1, len(psd1D)), dtype=np.uint8)
            histogram[height-psd1D, np.arange(len(psd1D))] = 255
            img_jpg = self.encode_jpg(histogram, 90)
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