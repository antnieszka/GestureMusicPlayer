import time
import cv2
import numpy as np
from subprocess import check_call

from commands import *


class TooDarkError(Exception):
    pass


def analyze_camera(cap):
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

        max_area = 0

        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if (area > max_area):
                max_area = area
                ci = i

        # find convex hulls using contours
        try:
            cnt = contours[ci]
        except Exception as e:
            raise TooDarkError(e)

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
        print("hulls = %s" % hull.shape[0])

        # compute defects using contours and hulls
        defects = cv2.convexityDefects(cnt, hull)
        print("defects = %s" % defects.shape[0])
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
        print(defects.shape[0] - 1)

        # show analyzed input/output
        cv2.imshow('output', drawing)
        cv2.imshow('input', img)

        k = cv2.waitKey(10)
        # got ESC key? if yes - exit!
        if k == 27:
            break

        # time.sleep(2)

if __name__ == '__main__':
    # just in case - reduce volume
    check_call(['vlc-ctrl', 'volume', '0.25'])
    cap = cv2.VideoCapture(0)
    analyze_camera(cap)
