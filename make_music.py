from utils import detector_utils as detector_utils
from gesture_detector import label_image as label_image
import cv2
import tensorflow as tf
import datetime
import argparse
from threading import Thread
from imutils.video import VideoStream
import imutils
import pyaudio
import sys, time
import numpy as np
import wave
import audioop
import multiprocessing

detection_graph, sess = detector_utils.load_inference_graph() # Load hand detection
gesture_sess, input_operation, output_operation = label_image.get_ready() # Load gesture detection

# Main Loop
def main(volume, pitch, pause):

    score_thresh = 0.2 # Hand detection center threshold
    fps = 1
    display = 1

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 180)

    # start_time = datetime.datetime.now()
    num_frames = 0
    im_width, im_height = (int(cap.get(3)), int(cap.get(4)))

    # max number of hands we want to detect/track
    num_hands_detect = 2
    window_name = '**MaKE yOuR OwN MUsiC**'

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        isPaused = False
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        ret, image_np = cap.read()
        image_np = cv2.flip(image_np, 1)

        try:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        except:
            print("Error converting to RGB")

        half_width = int(im_width/2)

        image_l = image_np[:, :half_width, :]
        image_r = image_np[:, half_width:im_width, :]

        # Hand detection
        boxes, scores = detector_utils.detect_objects(image_np, detection_graph, sess)
        centers, rects = detector_utils.find_center_of_hands(num_hands_detect, score_thresh,
                                         scores, boxes, im_width, im_height, image_np)

        # Threshold for gesture detection
        threshold = 0.9

        # if 2 hands are found
        if len(rects) > 2:
            # order: left, top, right, bottom, center x, center y
            hand1 = [int(rects[0][0]), int(rects[0][1]), int(rects[1][0]), int(rects[1][1]), int(centers[0][0]), int(centers[0][1])]
            hand2 = [int(rects[2][0]), int(rects[2][1]), int(rects[3][0]), int(rects[3][1]), int(centers[1][0]), int(centers[1][1])]

            if rects[0][0] > rects[2][0]:
                right = hand1
                left = hand2
            else:
                right = hand2
                left = hand1

            # check for left hand and right hand, amend audio accordingly
            if left[4] < half_width:
                volume.value = ((im_height-left[5])*8/im_height)
                handLeft = image_np[left[1]:left[3], left[0]:left[2], :]
                # cv2.imshow('Left', cv2.cvtColor(handLeft, cv2.COLOR_RGB2BGR))
                gesture, gesture_val = label_image.detect(gesture_sess, handLeft, input_operation, output_operation)
                isPaused = check_pause(gesture, gesture_val, threshold, image_np)
            if right[4] > half_width:
                pitch.value = (im_height-right[5])*1200/im_height-200
                handRight = image_np[right[1]:right[3], right[0]:right[2], :]
                # cv2.imshow('Right', cv2.cvtColor(handRight, cv2.COLOR_RGB2BGR))

        # if only 1 hand is found
        elif len(rects) > 0:
            hand = [int(rects[0][0]), int(rects[0][1]), int(rects[1][0]), int(rects[1][1]), int(centers[0][0]), int(centers[0][1])]
            handOnly = image_np[hand[1]:hand[3], hand[0]:hand[2], :]
            if hand[4] < half_width:
                volume.value = ((im_height-hand[5])*8/im_height)
                gesture, gesture_val = label_image.detect(gesture_sess, handOnly, input_operation, output_operation)
                isPaused = check_pause(gesture, gesture_val, threshold, image_np)
            elif hand[4] > half_width:
                pitch.value = (im_height-hand[5])*1200/im_height-200
            # cv2.imshow('only hand', cv2.cvtColor(handOnly, cv2.COLOR_RGB2BGR))

        pause.value = isPaused

        # add a line to split the screen
        cv2.line(image_np, (half_width,0),(half_width,im_height),(255, 255, 255), 1)

        if (display > 0):
            cv2.putText(image_np, "VOLUME: "+str(round(volume.value, 2)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            cv2.putText(image_np, "PITCH: "+str(pitch.value), (10+half_width, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            cv2.imshow(window_name, cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))

            if cv2.waitKey(5) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
        else:
            print("frames processed: ", num_frames, "elapsed time: ",
                  elapsed_time, "fps: ", str(int(fps)))

# Helper method to check whether or not music should be paused or not; returns boolean.
def check_pause(gesture, gesture_val, threshold, image_np):
    if int(gesture) == 0 and gesture_val > threshold:
        cv2.putText(image_np, "PAUSED", (120, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)
        return True
    return False

# Method to change audio
def audio(volume, pitch, pause):

    CHUNK = 2**14

    if len(sys.argv) < 2:
        print("Missing input wav file")
        sys.exit(-1)

    wf = wave.open(sys.argv[1], 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

    data = wf.readframes(CHUNK)

    while True:
        if data == b'' : # If file is over then rewind.
            wf.rewind()
            data = wf.readframes(CHUNK)

        if len(data) is not 0:
            data = np.frombuffer(data, np.int16)
            n = int(pitch.value)
            # Code to change pitch
            data = np.array(wave.struct.unpack("%dh"%(len(data)), data))
            data = np.fft.rfft(data)
            data2 = [0]*len(data)
            data_reduce = (len(data) - n)
            data_extend = (len(data) + n)
            if n >= 0:
                data2[n:len(data)] = data[0:data_reduce]
                data2[0:n] = data[data_reduce:len(data)]
            else:
                data2[0:data_extend] = data[-n:len(data)]
                data2[data_extend:len(data)] = data[0:-n]

            data = np.array(data2)
            data = np.fft.irfft(data)

            dataout = np.array(data, dtype='int16')
            output = wave.struct.pack("%dh"%(len(dataout)), *list(dataout))

        ################################ Code to change volume
            # print("vol: "+str(volume.value))
            if(pause.value == True):
                volume.value = 0
            newdata = audioop.mul(output, 2, volume.value)
        #################################

            stream.write(newdata)
            data = wf.readframes(CHUNK)

            # print("Volume: {}".format(volume.value))
            # print("Pitch: {}".format(pitch.value))

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == '__main__':

    volume = multiprocessing.Value('f')
    pitch = multiprocessing.Value('f')
    pause = multiprocessing.Value('b')

    pause.value = False
    volume.value = 1
    pitch.value = 5

    p1 = multiprocessing.Process(target=audio, args=(volume, pitch, pause))
    p1.start()
    main(volume, pitch, pause)
