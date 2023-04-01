import cv2
from flask import Flask, Response, render_template
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    camera = cv2.VideoCapture(0)

    # Set the resolution
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) #1280
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) #720

    # Set the refresh rate (fps)
    camera.set(cv2.CAP_PROP_FPS, 30)

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        #time.sleep(1 / 30)  # Sleep for the inverse of the fps to achieve the desired refresh rate

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
