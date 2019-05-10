# Making Music with Gesture Detection

# Setup
brew install portaudio

pip3 install -r requirements.txt

To run:

python3 makemusic.py a.wav

It will take about 5 seconds to load inference graphs after a hand has been detected: please wait for a while!

# Notes

Input .wav must be single-stream (only one channel).

To convert your own audio file to wav: https://audio.online-convert.com/convert-to-wav - make sure to select mono audio channel.


# Structure

Our main file is makemusic.py, which contains the audio logic and video stream upon which we perform hand detection.

