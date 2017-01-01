# Gesture Music Player

Command music with simple hand gestures. 

## How it works

- get image from camera
- convert to gray scale
- blur the image reduce noise (details of the image are unimportant)
- use threshold (low pass filter) to get black and white image
- analyze the received shape to find convex hull/convexity defects

### Credits and links

- Python bindings for VLC from: https://wiki.videolan.org/Python_bindings
- Python tool for controlling VLC https://github.com/amol9/vlc-ctrl
- Quora discussions: https://www.quora.com/What-is-the-easiest-way-to-recognise-gestures-in-OpenCV-using-Python
- Gesture-opencv project on GitHub https://github.com/vipul-sharma20/gesture-opencv
- WX non-blocking GUI: https://wiki.wxpython.org/Non-Blocking%20Gui
- Multithreading in TKinter: http://stackoverflow.com/questions/1198262/tkinter-locks-python-when-icon-loaded-and-tk-mainloop-in-a-thread

