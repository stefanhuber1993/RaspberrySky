#!/usr/bin/python2
import cv2
import time
from collections import deque
from threading import Thread
from subprocess import call


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


