from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from engineio.payload import Payload
from flask_sqlalchemy import SQLAlchemy
import os
import cv2 as cv
import numpy as np
import time
from subprocess import Popen

# Loading and warm-up OpenVINO-format YOLOv8n model
def model_warm_up():
    global model

    warm_up_img = cv.imread('./model_warmUp_35.jpg')
    warm_up_img = cv.cvtColor(warm_up_img, cv.COLOR_BGR2RGB)
    _ = model.predict(warm_up_img)

print('The process for model loading and warm-up: started')
clock_proc = Popen(['pv', '-t'])
os.environ['YOLO_VERBOSE'] = 'False'

from ultralytics import YOLO
model = YOLO(model='./best_openvino_model')

model_warm_up()
clock_proc.kill()
print('The process for model loading and warm-up: completed')

# Flask initialization
app_obj = Flask(__name__)
env_config = os.getenv('APP_SETTINGS', 'config.DevelopmentConfig')
app_obj.config.from_object(env_config)

# Flask-SQLAlchemy initialization
app_obj.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app_obj)

import db_model

# Falsk-SocketIO initialization
Payload.max_decode_packets = 500
connected_clients = set()
socketio = SocketIO(app_obj, cors_allowed_origins="*")

@app_obj.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

@socketio.on('connect')
def server_connect():
    sid = request.sid
    transport = request.environ.get('flask.socketio.transport')
    
    print(f'Server is connecting to client: True, sid: {sid}, transport: {transport}')

@socketio.on('raw_img')
def recieve_raw_img(bin_img):
    img = binImg_to_arrImg(bin_img)
    
    # Detect face
    img = detect_face(img)

    # Encode the processed image to be jpeg image
    encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 90]
    _, img = cv.imencode('.jpeg', img, encode_param)
    bin_img = img.tobytes()

    # Define register time to be sent to client
    second_register_time = time.time()
    format_register_time = time.ctime(second_register_time) # format_register_time is in type of string
    format_register_time = format_register_time.encode() # format_register_time is in type of UTF-8 binary
    
    emit('detected_img', [bin_img, format_register_time])

@socketio.on('confirm_yes')
def insert_to_db(data, debug=True):
    bin_img = data[0]
    img = binImg_to_arrImg(bin_img)
    register_time = data[1] # register_time is already in type of string.

    work_registry = db_model.Work_register_tb(registry_img=img, registry_time=register_time)
    db.session.add(work_registry)
    db.session.commit()

    if debug:
        print('Image and time are registered to database.')

def binImg_to_arrImg(bin_img):
    img = np.frombuffer(bin_img, dtype=np.uint8)
    img = cv.imdecode(img, cv.IMREAD_COLOR)

    return img

def detect_face(img):
    global model
    
    # results = model(img, stream=True)
    results = model(img, stream=True, device='intel:gpu')
    result = list(results)[0]
    if len(result.boxes.xywh) != 0:
        top_right = (int(result.boxes.xyxy[0][0]), int(result.boxes.xyxy[0][1]))
        top_left = (int(result.boxes.xyxy[0][2]), int(result.boxes.xyxy[0][3]))
        label_str = f'{result.names[int(result.boxes.cls[0])]}'
        
        if label_str == 'Issara (Kao)':
            color = (0, 0, 0)
        elif label_str == 'Non-employee':
            color = (255, 255, 255)

        cv.rectangle(img, top_right, top_left, (0, 255, 0), 3)
        cv.putText(img, label_str, (top_right[0], top_right[1] -10), cv.FONT_HERSHEY_PLAIN, 2, color, 3, cv.LINE_8)

    return img 

if __name__ == "__main__":
    print('Server started')

    if os.name == 'nt':
        socketio.run(app_obj, debug=app_obj.config['DEBUG'], port=5000, host='0.0.0.0', certfile='cert.pem', keyfile='key.pem') # This line introduces "ssl.SSLEOFError: EOF occurred in violation of protocol." To resolve such error must call monkey.patch_all() from gevent before. 