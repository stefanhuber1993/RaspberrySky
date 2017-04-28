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


def azimuthalAverage(image, center=None):
    """
    Calculate the azimuthally averaged radial profile.

    image - The 2D image
    center - The [x,y] pixel coordinates used as the center. The default is
             None, which then uses the center of the image (including
             fracitonal pixels).

    """
    # Calculate the indices from the image
    y, x = np.indices(image.shape)

    if not center:
        center = np.array([(x.max() - x.min()) / 2.0, (x.max() - x.min()) / 2.0])

    r = np.hypot(x - center[0], y - center[1])

    # Get sorted radii
    ind = np.argsort(r.flat)
    r_sorted = r.flat[ind]
    i_sorted = image.flat[ind]

    # Get the integer part of the radii (bin size = 1)
    r_int = r_sorted.astype(int)

    # Find all pixels that fall within each radial bin.
    deltar = r_int[1:] - r_int[:-1]  # Assumes all radii represented
    rind = np.where(deltar)[0]  # location of changed radius
    nr = rind[1:] - rind[:-1]  # number of radius bin

    # Cumulative sum to figure out sums for each radius bin
    csim = np.cumsum(i_sorted, dtype=float)
    tbin = csim[rind[1:]] - csim[rind[:-1]]

    radial_prof = tbin / nr

    return radial_prof


if __name__ == "__main__":
    pass
