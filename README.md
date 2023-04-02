# RPI-Video-Streaming

This code works on a Raspberry Pi 4 with a 64bit Pi OS and a Raspberry High Quality Camera module.

The code captures frames from the webcam using OpenCV, encodes them as JPEGs, and yields them to the Flask server.

Video stream is returned and rendered into a template of the index.html file that can be accessed on port 8000 at localhost.