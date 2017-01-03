# Gesture Music Player

Command music player (for now only VLC) with simple hand gestures. Supported commands:
- play
- pause
- next track
- previous track
- volume up (+10%)
- volume down (-10%)

![Imgur](http://i.imgur.com/pNa43PC.png)

## How it works

- Get image from camera
- Convert to gray scale
- Blur the image reduce noise (details of the image are unimportant)
- Use threshold (low pass filter) to get black and white image
- Analyze the received shape to find convex hull/convexity defects
- If in debug mode display visuals
- Send some info to Tk control window

### Requirements

- python (tested on 2.7.12, should work on other versions)
- OpenCV-Python >= 3.0 (more here: http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_tutorials.html, sometimes named as python-opencv package in system repositories)
- Tkinter (ussually comes with Python or as a addtional package)
- numpy
- vlc-ctrl (https://github.com/amol9/vlc-ctrl)

Pip-installable list:
```
numpy
vlc-ctrl
```

Tested on:

![openSUSE](https://en.opensuse.org/images/9/93/Opensuse_1-2.png)

### Credits and links

- Python bindings for VLC from: https://wiki.videolan.org/Python_bindings
- Python tool for controlling VLC https://github.com/amol9/vlc-ctrl
- Quora discussion: https://www.quora.com/What-is-the-easiest-way-to-recognise-gestures-in-OpenCV-using-Python
- Multithreading in TKinter: http://stackoverflow.com/questions/1198262/tkinter-locks-python-when-icon-loaded-and-tk-mainloop-in-a-thread
- OpenCV blog: http://vipulsharma20.blogspot.com/2015/03/gesture-recognition-using-opencv-python.html
