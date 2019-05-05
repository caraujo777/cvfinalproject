from utils import detector_utils as detector_utils
import cv2
import tensorflow as tf
import datetime
import argparse

from imutils.video import VideoStream
import imutils

detection_graph, sess = detector_utils.load_inference_graph()

if __name__ == '__main__':

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

        boxesL, scoresL = detector_utils.detect_objects(image_l,
                                                      detection_graph, sess)
        centersL, rectsL = detector_utils.find_center_of_hands(num_hands_detect, score_thresh,
                                         scoresL, boxesL, half_width, im_height, image_l)
        if len(rectsL) > 0:
            top = int(rectsL[0][0])
            left = int(rectsL[0][1])
            bottom = int(rectsL[1][0])
            right = int(rectsL[1][1])
            hand1 = image_l[left:right, top:bottom, :]
            cv2.imshow('Hand 1', cv2.cvtColor(hand1, cv2.COLOR_RGB2BGR))
        
        boxesR, scoresR = detector_utils.detect_objects(image_r,
                                                      detection_graph, sess)
        centersR, rectsR = detector_utils.find_center_of_hands(num_hands_detect, score_thresh,
                                         scoresR, boxesR, half_width, im_height, image_r)
        if len(rectsR) > 0:
            top = int(rectsR[0][0])
            left = int(rectsR[0][1])
            bottom = int(rectsR[1][0])
            right = int(rectsR[1][1])
            hand2 = image_r[left:right, top:bottom, :]
            cv2.imshow('Hand 2', cv2.cvtColor(hand2, cv2.COLOR_RGB2BGR))

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
