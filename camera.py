#!/usr/bin/python2
import cv2
import time
import numpy as np
from collections import deque
from threading import Thread
from scipy.ndimage import measurements

class Camera():
    def __init__(self, channel=0):
        # Prepare the camera
        self.channel = channel
        #self.cap = cv2.VideoCapture(channel)
        self.input_deque = deque(maxlen=30 * 60 * 5)
        self.frame = None
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
            c = Thread(target=self._capture, args=(self.input_deque, verbose))
            c.start()
        else:
            print("Failed Connection to Camera on /dev/video%s" % self.channel)


    def stop_capture(self):
        self.break_capture = True
        time.sleep(1)

    def _capture(self, deque, verbose):
        self.break_capture = False
        while not self.break_capture:
            #time.sleep(0.005)
            s, img = self.cap.read()
            if s:
                if verbose:
                    print("Frame %s captured with shape %sx%s"%(len(deque), img.shape[1],img.shape[0]),)
                #self.frame = img
                #print(id(self.input_deque))
                deque.append({
                    'time': time.time(),
                    'frame_raw': img})
                #print(self.input_deque[-1])
        self.cap.release()


    def get_frame(self):
        try:
            img = self.input_deque[-1]['frame_raw']
            img_jpg = self.encode_jpg(img, 95)
            return img_jpg
        except:
            #print('No image found')
            return ""


    def get_frame_cut(self):
        try:
            img = self.input_deque[-1]['frame_raw']
            img_bw = img.mean(2)
            thr = img_bw > img_bw.mean()*2.0
            labeled_array, num_features = measurements.label(thr)
            size = np.bincount(labeled_array.ravel())
            biggest_label = size[1:].argmax() + 1
            clump_mask = labeled_array == biggest_label

            B = np.argwhere(clump_mask)
            (ystart, xstart), (ystop, xstop) = B.min(0), B.max(0) + 1
            Atrim = img[ystart:ystop, xstart:xstop]

            if Atrim.size<64:
                print("Too small")
                raise AssertionError

            img_jpg = self.encode_jpg(Atrim, 95)

            #img_jpg = self.encode_jpg((255*thr.astype(np.float)).astype(np.uint8), 80)

            return img_jpg
        except:
            # print('No image found')
            return ""


    def get_nonsense(self):
        nonsense = (np.random.rand(120, 160, 3) * 255).astype(np.uint8)
        img_jpg = self.encode_jpg(nonsense, 50)
        return img_jpg

    def encode_jpg(self, img, qual):
        return cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, qual])[1].tostring()

    def __del__(self):
        self.break_capture = True
        time.sleep(1)
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