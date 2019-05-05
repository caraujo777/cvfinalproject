from utils import detector_utils as detector_utils
import cv2
import tensorflow as tf
import datetime
import argparse
from threading import Thread

from imutils.video import VideoStream
import imutils

import pyaudio
import sys
import numpy as np
import wave
import audioop

import multiprocessing

detection_graph, sess = detector_utils.load_inference_graph()

def main(volume, pitch):

    score_thresh = 0.2
    fps = 1
    num_workers = 4
    queue_size = 5
    display = 1

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 180)

    start_time = datetime.datetime.now()
    num_frames = 0
    im_width, im_height = (int(cap.get(3)), int(cap.get(4)))
    # max number of hands we want to detect/track
    num_hands_detect = 2

    cv2.namedWindow('Single-Threaded Detection', cv2.WINDOW_NORMAL)

    while True:
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        ret, image_np = cap.read()
        image_np = cv2.flip(image_np, 1)

        try:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        except:
            print("Error converting to RGB")

        half_width = 160
        image_l = image_np[:, :half_width, :]
        image_r = image_np[:, half_width:im_width, :]


        # Actual detection. Variable boxes contains the bounding box cordinates for hands detected,
        # while scores contains the confidence for each of these boxes.
        # Hint: If len(boxes) > 1 , you may assume you have found atleast one hand (within your score threshold)

        boxes, scores = detector_utils.detect_objects(image_np,
                                                      detection_graph, sess)
        centers, rects = detector_utils.find_center_of_hands(num_hands_detect, score_thresh,
                                         scores, boxes, im_width, im_height, image_np)
        if len(rects) > 2:
            print(rects)
            hand1 = [int(rects[0][0]), int(rects[0][1]), int(rects[1][0]), int(rects[1][1])]
            hand2 = [int(rects[2][0]), int(rects[2][1]), int(rects[3][0]), int(rects[3][1])]
            if rects[0][0] > rects[2][0]:
                right = hand1
                left = hand2
            else:
                right = hand2
                left = hand1
            if left[2] < half_width:
                handLeft = image_np[left[1]:left[3], left[0]:left[2], :]
                cv2.imshow('Left', cv2.cvtColor(handLeft, cv2.COLOR_RGB2BGR))
            if right[0] > half_width:
                handRight = image_np[right[1]:right[3], right[0]:right[2], :]
                cv2.imshow('Right', cv2.cvtColor(handRight, cv2.COLOR_RGB2BGR))
                volume.value = volume.value + 0.1
                pitch.value = pitch.value + 10

        # Calculate Frames per second (FPS)
        num_frames += 1
        elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
        fps = num_frames / elapsed_time

        # add a line to split the screen
        cv2.line(image_np, (half_width,0),(half_width,im_height),(255,0,0),2)

        if (display > 0):
            # Display FPS on frame
            if (fps > 0):
                detector_utils.draw_fps_on_image("FPS : " + str(int(fps)),
                                                 image_np)

            cv2.imshow('Single-Threaded Detection',
                       cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))

            if cv2.waitKey(5) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
        else:
            print("frames processed: ", num_frames, "elapsed time: ",
                  elapsed_time, "fps: ", str(int(fps)))



def audio(volume, pitch):
    CHUNK = 2**15

    if len(sys.argv) < 2:
        print("Missing input wav file")
        sys.exit(-1)

    wf = wave.open(sys.argv[1], 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

    n = 0
    data = wf.readframes(CHUNK)
    while data != '':
        data = np.frombuffer(data, np.int16)
        ################################## Code to change pitch
        data = np.array(wave.struct.unpack("%dh"%(len(data)), data))
        if len(data) is not 0:
            data = np.fft.rfft(data)
            data2 = [0]*len(data)
            if n >= 0:
                data2[n:len(data)] = data[0:(len(data)-n)]
                data2[0:n] = data[(len(data)-n):len(data)]
            else:
                data2[0:(len(data)+n)] = data[-n:len(data)]
                data2[(len(data)+n):len(data)] = data[0:-n]
    
            data = np.array(data2)
            data = np.fft.irfft(data)
    
            dataout = np.array(data, dtype='int16')
            output = wave.struct.pack("%dh"%(len(dataout)), *list(dataout)) 

        ################################ Code to change volume
            newdata = audioop.mul(output, 2, volume.value)
        #################################

            stream.write(newdata)
            data = wf.readframes(CHUNK)

            print("Volume: {}".format(volume.value)) 
            print("Pitch: {}".format(pitch.value)) 
    
    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == '__main__':
  
    volume = multiprocessing.Value('f') 
    pitch = multiprocessing.Value('f') 

    volume.value = 0
    pitch.value = 0

    p1 = multiprocessing.Process(target=audio, args=(volume, pitch))
    p1.start()
    main(volume, pitch)

