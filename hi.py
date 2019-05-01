import pyaudio
import wave
import sys
import numpy as np

def getNewWave(i, data):

    newdata = np.frombuffer(data, np.int8)
    print(type(newdata))
    # scaled = np.int8(newdata/np.max(np.abs(newdata)) * 500)
    # volume = float(i/100)  
    # f = -(float(i) * 10) + 700
    # newdata = np.fromstring(newdata, np.int8) / 10 * 5
    # scaled = np.int16(newdata/np.max(np.abs(newdata)) * 500)
    # newdata = (newdata * 0.95).astype(np.int8)
    return newdata

def main():

    CHUNK = 1024

    if len(sys.argv) < 2:
        print("Missing input wav file. File must have single channel")
        sys.exit(-1)

    wf = wave.open(sys.argv[1], 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=wf.getframerate(),
                    output=True, frames_per_buffer=CHUNK)

    data = wf.readframes(CHUNK)
    i = 0
    while data != '':
        stream.write(getNewWave(i, data))
        # placeholder
        i = i + 5
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    p.terminate()

main()