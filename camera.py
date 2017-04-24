#!/usr/bin/python2
import cv2
import time
import numpy as np
from collections import deque
from threading import Thread
#from multiprocessing import Process

class Camera():
    def __init__(self, channel=0):
        # Prepare the camera
        self.channel = channel
        self.cap = cv2.VideoCapture(channel)
        self.input_deque = deque(maxlen=30 * 60 * 5)
        self.frame = None
        self.break_capture = False
        print("Camera warming up ...")
        time.sleep(0.25)
        # Log Success
        if self.cap.isOpened():
            print("Successful Connection to Camera on /dev/video%s" % channel)
        else:
            print("Failed Connection to Camera on /dev/video%s" % channel)

    def set_channel(self, newchannel):
        print("Change from %s to %s" % (self.channel, newchannel))
        if int(newchannel) != self.channel:
            self.__del__()
            self.__init__(newchannel)

    def start_capture(self, verbose=False):
        c = Thread(target=self._capture, args=(self.input_deque, verbose))
        c.start()

    def stop_capture(self):
        self.break_capture = True

    def _capture(self, deque, verbose):
        self.break_capture = False
        while not self.break_capture:
            time.sleep(0.001)
            s, img = self.cap.read()
            if s:
                if verbose:
                    print("Frame %s captured with shape %sx%s"%(len(deque), img.shape[1],img.shape[0]))
                #self.frame = img
                #print(id(self.input_deque))
                deque.append({
                    'time': time.time(),
                    'frame_raw': img})
                #print(self.input_deque[-1])

    # def get_frame(self):
    #     result = [None]
    #     c = Thread(target=self._get_frame_worker, args=(self.input_deque, result))
    #     c.start()
    #     c.join()
    #     return result[0]
    #
    # def _get_frame_worker(self,  deque, result):
    #     if len(deque) > 0:
    #         img = deque[-1]['frame_raw']
    #         img_jpg = self.encode_jpg(img, 80)
    #         result[0] = img_jpg
    #     else:
    #         print('No image found')
    #         result[0] = ""

    def get_frame(self):
        if len(self.input_deque) > 0:
            img = self.input_deque[-1]['frame_raw']
            img_jpg = self.encode_jpg(img, 80)
            return img_jpg
        else:
            #print('No image found')
            return ""


    def get_nonsense(self):
        nonsense = (np.random.rand(120, 160, 3) * 255).astype(np.uint8)
        img_jpg = self.encode_jpg(nonsense, 50)
        return img_jpg

    def encode_jpg(self, img, qual):
        return cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, qual])[1].tostring()

    def __del__(self):
        self.break_capture = True
        time.sleep(0.25)
        self.cap.release()
        time.sleep(0.25)
        print("Camera Stream Released")
        return ()


if __name__ == "__main__":
    print("Making 10 Seconds of test capture")
    cam = Camera()
    cam.start_capture(verbose=False)
    for i in range(5):
        time.sleep(2)
        print(len(cam.input_deque))
        print("Last Frame is jpg str with length %s"%len(cam.get_frame()))
    cam.stop_capture()