import cv2
from flask import Flask, Response, render_template

app = Flask(__name__)

@app.route('/')
def index():

    return render_template('index.html')

def generate_frames():
    """
    The function `generate_frames` captures frames from the webcam using OpenCV, encodes them as JPEGs, and yields
    them to the Flask server.
    """
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    camera.set(cv2.CAP_PROP_FPS, 25)

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():

    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)