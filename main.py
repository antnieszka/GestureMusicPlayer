import math
import tkFont
import numpy as np
import cv2  # required 3+
import Tkinter as tk
import thread
import Queue
import time

from commands import *

request_queue = Queue.Queue()
result_queue = Queue.Queue()
t = None
debug = False
enable_commands = False
REALLY_NOT_DEBUG = True
COOLDOWN = 5
LAST_TIME = time.time()


def submit_to_tkinter(cb, *args, **kwargs):
    request_queue.put((cb, args, kwargs))
    return result_queue.get()


def debug_toggle():
    global debug
    debug = not debug


def toggle_commands():
    global enable_commands
    enable_commands = not enable_commands


def main_tk_thread():
    global t

    def timertick():
        try:
            cb, args, kwargs = request_queue.get_nowait()
        except Queue.Empty:
            pass
        else:  # if no exception was raised
            retval = cb(*args, **kwargs)
            result_queue.put(retval)
        # reschedule after some time
        t.after(10, timertick)

    # create main Tk window
    t = tk.Tk()
    t.title("Debug controls")
    t.geometry('%dx%d+%d+%d' % (320, 320, 850, 200))
    # set font for labels
    font = tkFont.Font(family="Arial", size=18, weight=tkFont.BOLD)
    # create buttons, labels
    tc = tk.Button(text='enable commands', name='ec', command=toggle_commands, width='15')
    tc.place(x=20, y=210)
    b = tk.Button(text='debug mode', name='dbg', command=debug_toggle, width='15')
    b.place(x=20, y=260)
    hull = tk.Label(t, name="hull", text="None", font=font)
    hull.place(x=20, y=10)
    defects = tk.Label(t, name="defects", text="None", font=font)
    defects.place(x=20, y=60)
    defects_filtered = tk.Label(t, name="defects_filtered", text="None", font=font)
    defects_filtered.place(x=20, y=110)
    command = tk.Label(t, name="command", text="None", font=font)
    command.place(x=20, y=160)
    en_command = tk.Label(t, name="en_command", text="None")
    en_command.place(x=160, y=215)
    en_dbg = tk.Label(t, name="en_dbg", text="None")
    en_dbg.place(x=160, y=265)
    # start timer a.k.a. scheduler
    timertick()
    # main Tk loop
    t.mainloop()


# setters for Tk GUI elements
def hull_label(a):
    t.children["hull"].configure(text=str("All hulls = %s " % a))


def defects_label(a):
    t.children["defects"].configure(text=str("All defects = %s" % a))


def defects_filtered_label(a):
    t.children["defects_filtered"].configure(text=str("Defects filtered = %s" % a))


def command_label(a):
    t.children["command"].configure(text=str("Command = %s" % a))


def en_command_label(a):
    t.children["en_command"].configure(text=str("(%s)" % a))


def en_dbg_label(a):
    t.children["en_dbg"].configure(text=str("(%s)" % a))


def check_command(c, exe):
    if c == 1:
        if REALLY_NOT_DEBUG and exe:
            play()
        return "PLAY"
    elif c == 2:
        if REALLY_NOT_DEBUG and exe:
            pause()
        return "PAUSE"
    elif c == 3:
        if REALLY_NOT_DEBUG and exe:
            move_next()
        return "NEXT"
    elif c == 4:
        if REALLY_NOT_DEBUG and exe:
            move_prev()
        return "PREVIOUS"
    elif c == 5:
        # if REALLY_NOT_DEBUG and exe:
        #     vol_down()
        return "VOLUME CONTROL (disabled)"
    return None


if __name__ == '__main__':
    thread.start_new_thread(main_tk_thread, ())

    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        # 1. Constructing Region Of Interest (ROI)
        # read frame from camera
        _, img = cap.read()
        # add rectangle for 'target scanning area' 300x300
        cv2.rectangle(img, (350, 350), (50, 50), (0, 255, 0), 0)
        # crop input image to 300x300
        crop_img = img[50:350, 50:350]
        # convert image to gray scale
        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        if debug:
            cv2.imshow('Gray scale', gray)
        # use Gaussian blur
        blur = cv2.GaussianBlur(src=gray, ksize=(35, 35), sigmaX=0)
        if debug:
            cv2.imshow('Blurred', blur)
        # apply threshold to get black and white (binary) image (ROI)
        _, thresh1 = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        if debug:
            cv2.imshow('Threshold', thresh1)

        # 2. Analyze ROI
        # find contours
        _, contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # _, contours, hierarchy = cv2.findContours(thresh1.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # get max contour area
        cnt = max(contours, key=lambda x: cv2.contourArea(x))

        # convex hull
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(crop_img, (x, y), (x + w, y + h), (0, 0, 255), 0)
        hull = cv2.convexHull(cnt)

        # contours
        drawing = np.zeros(crop_img.shape, np.uint8)
        cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 0)
        cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 0)
        hull = cv2.convexHull(cnt, returnPoints=False)

        # compute and plot convexity defects
        defects = cv2.convexityDefects(cnt, hull)
        count_defects = 0
        cv2.drawContours(thresh1, contours, -1, (0, 255, 0), 3)
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(cnt[s][0])
            end = tuple(cnt[e][0])
            far = tuple(cnt[f][0])
            # dist
            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57
            if angle <= 90:
                count_defects += 1
                cv2.circle(crop_img, far, 3, [255, 0, 0], -1)
            # dist = cv2.pointPolygonTest(cnt,far,True)
            cv2.line(crop_img, start, end, [0, 255, 0], 2)
            if debug:
                cv2.circle(crop_img, far, 5, [0, 0, 255], -1)

        # show analyzed input/output
        if debug:
            all_img = np.hstack((drawing, crop_img))
            cv2.imshow('Contours vs image', all_img)

        cv2.imshow('Input', img)

        k = cv2.waitKey(50)
        # got ESC key? if yes - exit!
        if k == 27:
            break
        elif k == 99:  # for 'c' toggle command execution
            print 'c input'
            toggle_commands()
        elif k == 100:  # for 'd' toggle debug mode
            print 'd input'
            debug_toggle()

        # do not 'change' command to quickly and wait after last one
        if time.time() - LAST_TIME > COOLDOWN and enable_commands:
            exe = True
            LAST_TIME = time.time()
        else:
            exe = False

        # check what command to execute and run it
        com = check_command(count_defects, exe)

        delta = time.time() - LAST_TIME
        to_next = COOLDOWN - delta
        if to_next < 0:
            to_next = 0
        # submit some data to GUI
        submit_to_tkinter(hull_label, str(hull.shape[0]))
        submit_to_tkinter(defects_label, str(defects.shape[0]))
        submit_to_tkinter(defects_filtered_label, str(count_defects))
        submit_to_tkinter(en_command_label, str("%s, cooldown %.2fs." % (enable_commands, to_next)))
        submit_to_tkinter(en_dbg_label, debug)
        if com:
            submit_to_tkinter(command_label, com)
