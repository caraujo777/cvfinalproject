import numpy as np
from imutils.video import VideoStream
import imutils
import cv2
import datetime
import imutils
import time

vs = VideoStream(src=0).start()
time.sleep(2.0)
firstFrame = None

while True:
	# grab the current frame and initialize the occupied/unoccupied
	# text
    frame = vs.read()
    frame = frame
    text = "no movement"

	# if the frame could not be grabbed, then we have reached the end
	# of the video
    if frame is None:
        break

	# resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    # blur to try and remove noise

	# if the first frame is none, initialise the background
    if firstFrame is None:
        firstFrame = gray
        continue

    # compute the absolute difference between the current frame and
	# first frame (ie background)
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

	# loop over the contours
    for c in cnts:
		# if the contour is too small, ignore it

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
        #experiment with 250!!
        if cv2.contourArea(c) < 250:
            continue
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "yep"
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    cv2.imshow("Feed", frame)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Frame Delta", frameDelta)
    key = cv2.waitKey(1) & 0xFF

	# if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break

# When everything done, release the capture
vs.release()
cv2.destroyAllWindows()
