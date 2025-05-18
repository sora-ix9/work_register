from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit
from engineio.payload import Payload
from flask_sqlalchemy import SQLAlchemy
import base64
import os
import cv2 as cv
import numpy as np
import time

os.environ['YOLO_VERBOSE'] = 'False'

from ultralytics import YOLO
# model = YOLO(model='best_YOLOv8n_model.pt')
model = YOLO(model='./best_openvino_model')

# Flask initialization
app = Flask(__name__)
env_config = os.getenv('APP_SETTINGS', 'config.DevelopmentConfig')
app.config.from_object(env_config)

# Flask-SQLAlchemy initialization
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

import db_model

# Falsk-SocketIO initialization
Payload.max_decode_packets = 500
connected_clients = set()
socketio = SocketIO(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

@socketio.on('connect')
def server_connect():
    sid = request.sid

    if sid in connected_clients:
        # print(f"Duplicate connection attempt: {sid}")
        disconnect()  # Optional
    else:
        connected_clients.add(sid)
        # print(f'Server is connecting to client: True, sid: {sid}')

@socketio.on('disconnect')
def server_disconnect():
    sid = request.sid
    connected_clients.discard(sid)
    # print(f"Client disconnected: {sid}")
    
@socketio.on('raw_img')
def recieve_raw_img(raw_img):
    # Decode base64 image data
    img = base64_to_img(raw_img)
    
    # Detect face
    img = detect_face(img)

    # Encode the processed image to be jpeg image
    encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 90]
    result, jpeg_img = cv.imencode('.jpeg', img, encode_param)
    
    # Encode the processed jpeg image to be base64 binary
    detected_img_base64bin = base64.b64encode(jpeg_img)

    # Encode the base64 binary of processed image to be base64 string
    detected_img_base64str = detected_img_base64bin.decode()

    # Define register time to be sent to client
    second_register_time = time.time()
    format_register_time = time.ctime(second_register_time) # format_register_time is in type of string
    format_register_time = format_register_time.encode('ascii') # format_register_time is in type of ascii-binary
    b64bin_format_register_time = base64.b64encode(format_register_time)
    b64str_format_register_time = b64bin_format_register_time.decode()

    # Define data URL that contains base-64 strings of both image and register time. 
    detectedImg_registerTime_URL = 'data:image/jpg;base64,' + detected_img_base64str + ',' + b64str_format_register_time

    # Send the processed image to the client
    emit('detected_img', detectedImg_registerTime_URL)

@socketio.on('confirm_yes')
def insert_to_db(detectedImg_registerTime_URL, debug=True):
    detectedImg_URL = detectedImg_registerTime_URL.split(',')[0] + ',' + detectedImg_registerTime_URL.split(',')[1]
    img = base64_to_img(detectedImg_URL)

    base64str_register_time = detectedImg_registerTime_URL.split(',')[2]
    register_time = str(base64.b64decode(base64str_register_time))



    work_registry = db_model.Work_register_tb(registry_img=img, registry_time=register_time)
    db.session.add(work_registry)
    db.session.commit()

    if debug:
        print('Register image and time are recoreded to database.')

def base64_to_img(base64_str):     
    # Extract the base64 binary from the base64 string
    base64_str = base64_str.split(',')[1]
    
    # Decode the base64 binary to image binary  
    img_bin = base64.b64decode(base64_str)

    # Convert the image binary to image array
    img_arr = np.frombuffer(img_bin, dtype=np.uint8)
    
    # Decode the image array being on memory to rgb image, this is efficient when loding image from the internet 
    img = cv.imdecode(img_arr, cv.IMREAD_COLOR)
    # img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    return img

def detect_face(img):
    global model
    
    # results = model(img, stream=True)
    results = model(img, stream=True, device='intel:gpu')

    for r in results:
        if len(r.boxes.xywh) != 0:
            top_right = (int(r.boxes.xyxy[0][0]), int(r.boxes.xyxy[0][1]))
            top_left = (int(r.boxes.xyxy[0][2]), int(r.boxes.xyxy[0][3]))
            label_str = f'{r.names[int(r.boxes.cls[0])]}'
            cv.rectangle(img, top_right, top_left, (0, 255, 0), 3)
            cv.putText(img, label_str, (top_right[0], top_right[1] -10), cv.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3, cv.LINE_8)

    return img 

if __name__ == "__main__":
    context = ('cert.pem', 'key.pem')
    socketio.run(app, debug=app.config['DEBUG'], port=5000, host='0.0.0.0', ssl_context=context)