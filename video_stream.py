import os
import cv2
import logging
import threading
from flask import Flask, Response, render_template, request
from functools import wraps

logging.basicConfig(filename='video_stream.log', level=logging.DEBUG)

app = Flask(__name__)

USERNAME = os.getenv('FLASK_USERNAME')
PASSWORD = os.getenv('FLASK_PASSWORD')

if not USERNAME or not PASSWORD:
    logging.error('FLASK_USERNAME and FLASK_PASSWORD must be set in environment')
    raise SystemExit(1)

camera_instance = None
camera_lock = threading.Lock()

def get_camera():
    global camera_instance
    with camera_lock:
        if camera_instance is None or not camera_instance.isOpened():
            try:
                logging.info('Initializing GStreamer libcamerasrc pipeline for IMX477')
                gst_pipeline = (
                    'libcamerasrc ! '
                    'video/x-raw,width=1280,height=720,framerate=25/1 ! '
                    'videoconvert ! '
                    'video/x-raw,format=BGR ! '
                    'appsink drop=true max-buffers=1'
                )
                camera_instance = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
                
                if not camera_instance.isOpened():
                    logging.error('Failed to open GStreamer pipeline')
                    return None
                    
                logging.info('GStreamer pipeline opened successfully')
                
            except Exception as e:
                logging.exception('Error initializing GStreamer pipeline: %s', e)
                return None
                
        return camera_instance

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@requires_auth
def index():
    return render_template('index.html')

def generate_frames(camera):
    try:
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        camera.set(cv2.CAP_PROP_FPS, 25)
        camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]

        while True:
            success, frame = camera.read()
            if not success:
                logging.error('Failed to read frame from camera')
                break

            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            if not ret:
                logging.error('Failed to encode frame to JPEG')
                continue

            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        try:
            camera.release()
        except Exception as e:
            logging.exception('Error releasing camera: %s', e)

@app.route('/video_feed')
@requires_auth
def video_feed():
    camera = get_camera()
    if camera is None:
        return Response('Camera unavailable', status=503)

    return Response(generate_frames(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
