import time
import socket
import pandas as pd
import numpy as np
import cv2
from joblib import load

# ---------------------------
# Parameters & Setup
# ---------------------------
HOST = "0.0.0.0"       # Listen on all interfaces
PORT = 5001            # Must match the Arduino code
fs = 50                # Expected sampling frequency (samples per second)
window_size_sec = 2    # Window length in seconds (e.g., 2 sec)
window_size = fs * window_size_sec  # e.g., 100 samples
step_size = window_size // 2        # 50% overlap (e.g., 50 samples)
sensor_cols = ["Acce_x", "Acce_y", "Acce_z", "Gyro_x", "Gyro_y", "Gyro_z"]

trigger_times = 3  # Number of consecutive identical predictions needed

# Load your pre-trained classification model
model = load("model/exercise_model.joblib")

# Map each exercise label to a video file path (adjust paths as needed)
video_media = {
    "BicepCurl": "videos/BicepCurl.mp4",
    "LateralRaise": "videos/LateralRaise.mp4",
    "OverHead": "videos/OverHead.mp4",
    "Plank": "videos/Plank.mp4",
    "Pull": "videos/Pull.mp4",
    "PushUp": "videos/PushUp.mp4",
    "TricepExtension": "videos/TricepExtension.mp4",
    "WristCurl": "videos/WristCurl.mp4"
}

# ---------------------------
# Create TCP Server
# ---------------------------
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print("Waiting for connection on port", PORT)

conn, addr = server_socket.accept()
print("Connected by", addr)

buffer = []
prev_prediction = None
consecutive_count = 0

# ---------------------------
# Feature Extraction Function
# ---------------------------
def extract_features(window_df):
    features = {}
    for col in sensor_cols:
        arr = window_df[col].values.astype(np.float64)
        features[f"{col}_mean"]   = np.mean(arr)
        features[f"{col}_std"]    = np.std(arr)
        features[f"{col}_min"]    = np.min(arr)
        features[f"{col}_max"]    = np.max(arr)
        features[f"{col}_energy"] = np.sum(np.square(arr)) / len(arr)
    return features

# ---------------------------
# Video Playing Function
# ---------------------------
def play_video(video_path, desired_size=640):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video", video_path)
        return
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # Resize the frame to a fixed square size (e.g., 640x640)
        frame = cv2.resize(frame, (desired_size, desired_size))
        cv2.imshow("Exercise Video", frame)
        # Wait 25ms between frames; exit if 'q' is pressed
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyWindow("Exercise Video")

# ---------------------------
# Real-Time Classification Loop
# ---------------------------
print("Starting real-time classification. Perform your exercise!")
while True:
    try:
        data = conn.recv(1024)
        if not data:
            break
        # Decode and split data into lines
        lines = data.decode('utf-8').strip().splitlines()
        for line in lines:
            parts = line.split(',')
            # Expecting at least 7 parts: 6 sensor values + an extra value (e.g., grip) if available.
            # Here we only use the first 6 sensor values.
            if len(parts) >= 7:
                data_point = {sensor_cols[i]: float(parts[i]) for i in range(6)}
                grid_type = parts[6]  # This is the extra value (e.g., grip)
                buffer.append(data_point)
    except Exception as e:
        print("Error processing data:", e)
    
    if len(buffer) >= window_size:
        window_df = pd.DataFrame(buffer[:window_size])
        feat = extract_features(window_df)
        feature_vector = np.array(list(feat.values())).reshape(1, -1)
        # Feature_vector will contain the IMU values and the grid type
        prediction = model.predict(feature_vector)[0]
        print("Real-time Prediction:", prediction)
        
        # Update consecutive prediction count
        if prediction == prev_prediction:
            consecutive_count += 1
        else:
            consecutive_count = 1
            prev_prediction = prediction
        
        # If the same prediction appears trigger_times in a row, play the corresponding video
        if consecutive_count >= trigger_times:
            print("Consistent prediction detected. Playing video for:", prediction)
            if prediction in video_media:
                play_video(video_media[prediction])
            else:
                print("No video available for", prediction)
            # Reset the consecutive count after playing the video
            consecutive_count = 0
        
        # Slide the window (50% overlap)
        buffer = buffer[step_size:]
    
    time.sleep(0.01)
