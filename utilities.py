import numpy as np


def pad_to_ratio(array, aspect):
    height, width = array.shape[0:2]
    array_aspect = width/float(height)
    aspect_change = array_aspect / aspect
    if aspect_change >= 1.0:
        missing_pixels = int(np.around((aspect_change - 1.0) * height / 2.0))
        newarray = np.pad(array, [[missing_pixels, missing_pixels], [0, 0], [0, 0]], mode='constant')
    if aspect_change < 1.0:
        missing_pixels = int(np.around((1.0/aspect_change - 1.0) * width / 2.0))
        newarray = np.pad(array, [[0, 0], [missing_pixels, missing_pixels], [0, 0]], mode='constant')
    return newarray


if __name__ == "__main__":
    A = (np.abs(np.random.randn(100,100,3))*100).astype(np.uint8)
    print(A.mean())
    print(A.dtype)
    A_pad = pad_to_ratio(A, 4.0/3.0)
    print(A_pad.mean())
    s = A_pad.shape
    print(s[1]/float(s[0]))
    print(A_pad.dtype)
