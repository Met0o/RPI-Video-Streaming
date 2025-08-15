# RPI-Video-Streaming

This code works on a Raspberry Pi 4 with a 64bit Pi OS and a Raspberry High Quality Camera module (IMX477).

The code captures frames from the camera using OpenCV with a GStreamer libcamerasrc pipeline, encodes them as JPEGs, and yields them to the Flask server.

Video stream is returned and rendered into a template of the index.html file that can be accessed on port 8001.

## Architecture
- **Camera Backend**: GStreamer libcamerasrc pipeline (not V4L2) for reliable IMX477 support
- **Frame Processing**: OpenCV with GStreamer backend for frame capture and encoding
- **Web Server**: Flask with Gunicorn, using singleton camera instance to prevent conflicts
- **Authentication**: Basic HTTP authentication required for all endpoints

## Prerequisites
- Raspberry Pi 4 with 64-bit Pi OS
- IMX477 High Quality Camera module (or compatible CSI camera)

## To set up the local environment:
    * sudo apt-get update
    * sudo apt-get install -y gunicorn gstreamer1.0-libcamera gstreamer1.0-tools
    * pip install opencv-python-headless flask gunicorn
    * Set `FLASK_USERNAME` and `FLASK_PASSWORD` environment variables

## Recommended serving (without TLS termination):

    * FLASK_USERNAME=user_name_here FLASK_PASSWORD=password_here python3 -m gunicorn -w 1 --threads 2 --timeout 0 -b 0.0.0.0:8001 video_stream:app

## To auto-start the service on boot:

    * sudo nano /etc/systemd/system/rpi_video_stream.service
    
    [Unit]
    Description=Raspberry Pi Video Stream
    After=network-online.target
    Wants=network-online.target

    [Service]
    Type=simple
    User=user_name_here
    WorkingDirectory=/home/user_name_here/dev/RPI-Video-Streaming
    Environment="FLASK_USERNAME=user_name_here"
    Environment="FLASK_PASSWORD=password_here"
    Environment="PYTHONUNBUFFERED=1"
    ExecStart=/usr/bin/python3 -m gunicorn -w 1 --threads 2 --timeout 0 -b 0.0.0.0:8001 video_stream:app
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
    * Check the last 10 events in the service logs - sudo journalctl -u rpi_video_stream.service -n 10

## Troubleshooting

### Camera Issues
- **"Camera unavailable"**: Ensure camera is connected, enabled in raspi-config, and accessible
- **Blank white screen**: Check service logs for GStreamer pipeline errors

### Camera Detection
- Verify camera detection: `rpicam-hello --list-cameras`
- Check for camera devices: `ls -l /dev/video*`
- Test camera access: `rpicam-jpeg -o /tmp/test.jpg`

### Service Issues
- Check service status: `sudo systemctl status rpi_video_stream.service`
- View logs: `sudo journalctl -u rpi_video_stream.service -f`
- Verify port availability: `sudo ss -ltnp '( sport = :8001 )'`
