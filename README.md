# RPI-Video-Streaming

This code works on a Raspberry Pi 4 with a 64bit Pi OS and a Raspberry High Quality Camera module.

The code captures frames from the webcam using OpenCV, encodes them as JPEGs, and yields them to the Flask server.

Video stream is returned and rendered into a template of the index.html file that can be accessed on port 8000 at localhost.

To set up the local environment:

    * sudo apt-get update
    * pip install opencv-python-headless flask
        - In case of errors enable legacy camera and reboot: sudo raspi-config (probably not required for OpenCV)

To auto-start the service on boot:

    * sudo nano /etc/systemd/system/rpi_video_stream.service
    
    * [Unit]
      Description=Raspberry Pi Video Stream
      After=network.target

      [Service]
      User=username
      WorkingDirectory=/path/to/app
      ExecStart=/usr/bin/python3 /path/to/app/app.py
      Environment="FLASK_USERNAME=username"
      Environment="FLASK_PASSWORD=password"
      Restart=always
      RestartSec=5

      [Install]
      WantedBy=multi-user.target

    * sudo systemctl daemon-reload
    * sudo systemctl restart rpi_video_stream.service
    
    * Check the status - sudo systemctl status rpi_video_stream.service
    * Enable autostart - sudo systemctl enable rpi_video_stream.service
    * Disable autostart - sudo systemctl disable rpi_video_stream.service
    * Stop the service - sudo systemctl stop rpi_video_stream.service
    * Check the last 100 events in the service logs - sudo journalctl -u rpi_video_stream.service -n 100
