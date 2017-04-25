# RaspberrySky - WIP
A webserver for Raspberry Pi for using a webcam with a teleskope.


## Usage
Start web.py on Raspberry Pi or at Laptop attached to webcam attached to telescope. Will open server on 0.0.0.0:5000.
Access this address with browser on Raspberry Sky (or over local network).

## Dependencies
python 2.7, opencv

## Features
* Choice of Webcam, e.g. /dev/video0
* Live view of webcam image
* Live magnification view of imaged planet.

## TODO
* Server serve at IP open to local network
* Clean up browser interface

## Future Features
* Choice of Exposure Time
* Live computation of image histogram and fourier spectrum
* Live computation of "best of" image from the stream, e.g. best image of planet in last 10 seconds.
