import pyaudio
import sys
import numpy as np
import wave
import audioop

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

n = 1000

#range 1000 to -200

data = wf.readframes(CHUNK)
i = 0
# n and i will later be Y values of the two hand positions. Need to set range for both
while data != '':
    n = n - 50
    print(n)
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
        newdata = audioop.mul(data, 2, i)
        i = i + 0.1
    #################################

        stream.write(newdata)
        data = wf.readframes(CHUNK)
 
stream.stop_stream()
stream.close()
p.terminate()
