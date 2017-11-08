from scipy import fftpack
import numpy as np
from utilities import pad_to_ratio, azimuthalAverage, extract_largest_components
import cv2


class StreamAnalyser():
	def __init__(self, camera):
		self.camera = camera

	def empty_when_exception(func):
		def wrapper(self):
			try:
				return func(self)
			except Exception as e:
				print(e)
				return ''
		return wrapper

	@empty_when_exception
	def get_frame(self):
		img = self.camera.input_deque[-1]['frame_raw']
		img_jpg = self.encode_jpg(img, 95)
		return img_jpg

	@empty_when_exception
	def get_average_preview(self):
		pass
	
	@empty_when_exception
	def get_frame_focuspeak(self):
		img = self.camera.input_deque[-1]['frame_raw']
		img_bw = img.mean(2)
		binning_factor = 2

		img_view = img_bw.reshape(img.shape[0]//binning_factor, binning_factor,
								  img.shape[1]//binning_factor, binning_factor)
		img_binned = img_view[:,0,:,0]

		sobel_x = cv2.Sobel(img_binned, cv2.CV_64F, 1, 0, ksize=1)#.mean(2)
		sobel_y = cv2.Sobel(img_binned, cv2.CV_64F, 0, 1, ksize=1)#.mean(2)
		both = np.sqrt(sobel_x**2 + sobel_y**2)

		bloat = np.repeat(np.repeat(both,binning_factor, axis=0),binning_factor, axis=1)

		low, high = img_binned.min(), img_binned.max()
		contrast = high-low

		colored_img = np.copy(img)
		colored_img[bloat > 0.2*contrast] = [0, 255, 191]
		colored_img[bloat > 0.4*contrast] = [0, 191, 255]
		colored_img[bloat > 0.6*contrast] = [0, 64, 255]
		colored_img[bloat > 0.8*contrast] = [0, 0, 255]

		img_jpg = self.encode_jpg(colored_img, 80)
		return img_jpg

	@empty_when_exception
	def get_frame_cut(self):
			img = self.camera.input_deque[-1]['frame_raw']
			img_trim = extract_largest_components(img)
			if img_trim.size < 16 ** 2:
				return ""
			img_trim_aspect_corr = pad_to_ratio(img_trim, 4.0 / 3.0)
			img_jpg = self.encode_jpg(img_trim_aspect_corr, 95)
			return img_jpg

	@empty_when_exception
	def get_frame_hist(self):
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
		img_jpg = self.encode_jpg(histogram, 30)
		return img_jpg
			
	@empty_when_exception
	def get_frame_power(self):
		img = self.camera.input_deque[-1]['frame_raw'].mean(2).astype(np.uint8)
		F1 = fftpack.fft2(img)
		F2 = fftpack.fftshift(F1)
		psd2D = np.log(np.abs(F2) ** 2)
		psd1D = azimuthalAverage(psd2D).astype(float)
		psd1D /= np.percentile(psd1D, 100)
		psd1D = np.clip(psd1D, 0,1)
		height = int(len(psd1D)*0.75-1)
		psd1D *= float(height)
		psd1D = psd1D.astype(np.int)
		histogram = np.zeros((height+1, len(psd1D)), dtype=np.uint8)
		histogram[height-psd1D, np.arange(len(psd1D))] = 255
		img_jpg = self.encode_jpg(histogram, 30)
		return img_jpg

	@empty_when_exception
	def get_nonsense(self):
		nonsense = (np.random.rand(120, 160, 3) * 255).astype(np.uint8)
		img_jpg = self.encode_jpg(nonsense, 50)
		return img_jpg

	@staticmethod
	def encode_jpg(img, qual):
		return cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, qual])[1].tostring()
