import tkFont
import numpy as np
import cv2
from subprocess import check_call
import Tkinter as tk
import thread
import Queue
import sys

import Camera
from commands import *

request_queue = Queue.Queue()
result_queue = Queue.Queue()
t = None


def submit_to_tkinter(callable, *args, **kwargs):
    request_queue.put((callable, args, kwargs))
    return result_queue.get()


def main_tk_thread():
    global t

    def timertick():
        try:
            callable, args, kwargs = request_queue.get_nowait()
        except Queue.Empty:
            pass
        else:
            # print "something in queue"
            retval = callable(*args, **kwargs)
            result_queue.put(retval)

        t.after(10, timertick)

    t = tk.Tk()
    text = tk.Text()
    font = tkFont.Font(family="Arial", size=18, weight=tkFont.BOLD)
    t.configure(width=320, height=320)
    # b = tk.Button(text='test', name='button', command=tk._exit)
    # b.place(x=0, y=0)
    hull = tk.Label(t, name="hull", text="None", font=font)
    hull.place(x=20, y=10)
    defects = tk.Label(t, name="defects", text="None", font=font)
    defects.place(x=20, y=60)
    command = tk.Label(t, name="command", text="None", font=font)
    command.place(x=20, y=110)
    timertick()
    t.mainloop()


def hull_label(a):
    t.children["hull"].configure(text=str("Hull = %s " % a))


def defects_label(a):
    t.children["defects"].configure(text=str("Defects = %s" % a))


def command_label(a):
    t.children["command"].configure(text=str("Command = %s" % a))


if __name__ == '__main__':
    thread.start_new_thread(main_tk_thread, ())

    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        # 1. Constructing Region Of Interest (ROI)
        # read frame from camera
        _, img = cap.read()
        # convert image to gray scale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # use Gaussian blur
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # apply threshold to get black and white (binary) image (ROI)
        _, thresh1 = cv2.threshold(blur, 70, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # 2. Analyze ROI
        # find contours
        _, contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # empty matrix for output data to show later
        drawing = np.zeros(img.shape, np.uint8)

        # get max area
        max_area = 0
        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if area > max_area:
                max_area = area
                ci = i

        try:
            # get selected set of contours (biggest area)
            cnt = contours[ci]
        except Exception as e:
            raise Camera.TooDarkError(e)

        # find convex hulls using contours
        hull = cv2.convexHull(cnt)
        moments = cv2.moments(cnt)
        if moments['m00'] != 0:
            cx = int(moments['m10'] / moments['m00'])  # cx = M10/M00
            cy = int(moments['m01'] / moments['m00'])  # cy = M01/M00

        # plot output contours to show
        centr = (cx, cy)  # center point of ROI
        cv2.circle(img, centr, 5, [0, 0, 255], 2)
        cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 2)
        cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 2)

        cnt = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
        hull = cv2.convexHull(cnt, returnPoints=False)
        # print("hulls = %s" % hull.shape[0])

        # compute defects using contours and hulls
        defects = cv2.convexityDefects(cnt, hull)
        # print("defects = %s" % defects.shape[0])
        mind = 0
        maxd = 0

        # plot convexity defects
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(cnt[s][0])
            end = tuple(cnt[e][0])
            far = tuple(cnt[f][0])
            dist = cv2.pointPolygonTest(cnt, centr, True)
            cv2.line(img, start, end, [0, 255, 0], 2)
            cv2.circle(img, far, 5, [0, 0, 255], -1)
        # print(defects.shape[0] - 1)

        # show analyzed input/output
        cv2.imshow('output', drawing)
        cv2.imshow('input', img)

        com = False
        df = defects.shape[0]
        if df == 6:
            df = "VOLUME UP"
            # vol_up()
        elif df == 5:
            com = "PLAY"
            # play()
        elif df == 4:
            com = "PAUSE"
            # pause()
        elif df == 3:
            com = "NEXT"
            move_next()
        elif df == 2:
            com = "PREVIOUS"
            # move_prev()

        k = cv2.waitKey(100)
        # got ESC key? if yes - exit!
        if k == 27:
            break

        submit_to_tkinter(hull_label, str(hull.shape[0]))
        submit_to_tkinter(defects_label, str(defects.shape[0]))
        if com:
            submit_to_tkinter(command_label, com)
