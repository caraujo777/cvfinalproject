# import pyaudio
# import wave
# import sys
# import numpy as np
# from subprocess import call

# def getNewWave(i, data):
#     newdata = np.frombuffer(data, np.int8)
#     # scaled = np.int8(newdata/np.max(np.abs(newdata)) * 500)
#     # volume = float(i/100)  
#     # f = -(float(i) * 10) + 700
#     # newdata = np.fromstring(newdata, np.int8) / 10 * 5
#     # scaled = np.int16(newdata/np.max(np.abs(newdata)) * 500)
#     # newdata = (newdata * 0.95).astype(np.int8)
#     return newdata

# def main():

#     CHUNK = 2**16

#     n = 7

#     if len(sys.argv) < 2:
#         print("Missing input wav file. File must also have single channel")
#         sys.exit(-1)

#     wf = wave.open(sys.argv[1], 'rb')
#     p = pyaudio.PyAudio()

#     stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
#                 channels=wf.getnchannels(),
#                 rate=wf.getframerate(),
#                 output=True)

#     data = wf.readframes(CHUNK)
#     i = 0.0
#     while data != '':
#         # stream.write(getNewWave(i, data))
#         # i = i + 0.1
#         # print(i)
#         data = np.frombuffer(data, np.int16)
#         data = np.fft.rfft(data)
   
#         # This does the shifting
#         data2 = [0]*len(data)
#         if n >= 0:
#             data2[n:len(data)] = data[0:(len(data)-n)]
#             data2[0:n] = data[(len(data)-n):len(data)]
#         else:
#             data2[0:(len(data)+n)] = data[-n:len(data)]
#             data2[(len(data)+n):len(data)] = data[0:-n]
   
#         data = np.array(data2)
#         # Done shifting
   
#         # inverse transform to get back to temporal data
#         data = np.fft.irfft(data)
   
#         dataout = np.array(data, dtype='int16')
#         chunkout = wave.struct.pack("%dh"%(len(dataout)), *list(dataout))
#         stream.write(chunkout)
#         data = wf.readframes(CHUNK)

#     stream.stop_stream()
#     stream.close()
#     p.terminate()

# main()

import pyaudio
import sys, time
import numpy as np
import wave

CHUNK = 2**18

if len(sys.argv) < 2:
    print("Missing input wav file. File must also have single channel")
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')
p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True)

n = 500

data = wf.readframes(CHUNK)
while data != '':
    n = n - 100
    print(n)
    data = np.frombuffer(data, np.int16)
    data = np.array(wave.struct.unpack("%dh"%(len(data)), data))
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
    output = wave.struct.pack("%dh"%(len(dataout)), *list(dataout)) #convert back to 16-bit data

    

    stream.write(output)
    data = wf.readframes(CHUNK)
 
stream.stop_stream()
stream.close()
p.terminate()
