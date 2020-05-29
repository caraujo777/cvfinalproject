# Making Music with Gesture Detection

This app uses your webcam to detect your hand gestures and allows you  to create your own music at no cost. 

## Setup
```brew install portaudio```

```pip3 install -r requirements.txt```

**To run:**

```python3 make_music.py a.wav```

or

```python3 make_music.py <single stream .wav file>```

The ```a.wav``` is the audio file you are making the music based off of. The ```a.wav``` we provide in our directory is a single constant note. It will be played infinitely in the app so you can make any simple tunes with it.

It will take about 5 seconds to load the inference graphs for gesture detection after your left hand has been detected: please wait patiently for a while!

## How to Play


The screen is splitted into left and right - place your left hand in the left frame and your right hand in the right, then you can start making the moves and the music will come along!

* **Change Pitch:** move your right hand up/down
* **Change Volume:** move your left hand up/down
* **To Pause:** close your left hand (show fist)
* **To Resume:** open your left hand (show palm)
* **To Quit:** ```Ctrl+C``` in the terminal

## Notes

Input .wav must be single-stream (only one channel).

To convert your own audio file to wav: 

<https://audio.online-convert.com/convert-to-wav> 

Make sure to select mono audio channel.


## Structure

Our main file is make_music.py, which contains the audio logic and video stream upon which we perform hand detection.
Within utils, we have a WebcamVideoStream object detection set up.
Within gesture detector, we have helper classes for detecting open vs closed palms.

