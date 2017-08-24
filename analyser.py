from scipy import fftpack
import numpy as np
from scipy.ndimage import measurements
from utilities import pad_to_ratio, azimuthalAverage


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

    def get_frame_focuspeak(self):
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