from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
from keras.preprocessing import image
from keras.models import load_model
import pandas as pd

app = Flask(__name__)

model = load_model('best_model.h5') 

# Load Haar Cascade for face detection
face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_haar_cascade = cv2.CascadeClassifier(face_cascade_path)

# Start webcam
cap = cv2.VideoCapture(0)

# Buffer to store recent predictions
prediction_buffer = []

# Emotion playlists
emotion_dict = {0: "angry", 1: "disgust", 2: "happy", 3: "neutral", 4: "sad", 5: "surprise"}

# Load CSV files for each emotion
csv_files = {emotion: f'top_tracks/{emotion}_top_tracks.csv' for emotion in emotion_dict.values()}
dataframes = {emotion: pd.read_csv(csv_file) for emotion, csv_file in csv_files.items()}

def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        valid, test_image = cap.read()
        if not valid:
            break
        gray_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)

        faces_detected = face_haar_cascade.detectMultiScale(gray_image, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces_detected:
            if w * h > 500:  # Filter out small detected faces
                roi_gray = gray_image[y:y + h, x:x + w]
                roi_gray = cv2.resize(roi_gray, (48, 48))
                image_pixels = image.img_to_array(roi_gray)
                image_pixels = np.expand_dims(image_pixels, axis=0)
                predictions = model.predict(image_pixels)

                if len(predictions) > 0:
                    max_index = np.argmax(predictions[0])
                    emotion_prediction = emotion_dict[max_index]
                    prediction_buffer.append(emotion_prediction)
                    buffer_size = 5
                    if len(prediction_buffer) > buffer_size:
                        prediction_buffer.pop(0)
                    majority_emotion = max(set(prediction_buffer), key=prediction_buffer.count)
                    cv2.putText(test_image, majority_emotion, (int(x), int(y)),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

        # Encode frame into memory buffer, then decode into bytes
        ret, buffer = cv2.imencode('.jpg', test_image)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/recommendations')
def recommendations():
    if len(prediction_buffer) > 0:
        majority_emotion = max(set(prediction_buffer), key=prediction_buffer.count)
        if majority_emotion in dataframes:
            recommendations = dataframes[majority_emotion].head(10).to_dict('records')
            return jsonify(recommendations)
    return jsonify([])

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8083)
