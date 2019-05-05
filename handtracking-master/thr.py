from utils import detector_utils as detector_utils
import cv2
import tensorflow as tf
import datetime
import argparse
import pyaudio
import sys
import numpy as np
import wave
import audioop
from threading import Thread

from imutils.video import VideoStream
import imutils

# detection_graph, sess = detector_utils.load_inference_graph()

currentVolume = 1.0

# if __name__ == '__main__':
def thread1(mainthread):
    currentVolume += 0.001


def thread2(audiothread):
    CHUNK = 2**15

    # if len(sys.argv) < 2:
    #     print("Missing input wav file")
    #     sys.exit(-1)

    wf = wave.open("single_queen.wav", 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

    n = 1000

    global currentVolume

    data = wf.readframes(CHUNK)
    i = 0
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
            newdata = audioop.mul(output, 2, currentVolume)
            print(currentVolume)
        #################################

            stream.write(newdata)
            data = wf.readframes(CHUNK)
    
    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == '__main__':
    thread1 = Thread( target=thread1, args=("Thread-1", ) )
    thread2 = Thread( target=thread2, args=("Thread-2", ) )

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
