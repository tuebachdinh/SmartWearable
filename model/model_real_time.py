import socket
import time
import pandas as pd
import numpy as np
from joblib import load

# ---------------------------
# Parameters
# ---------------------------
HOST = "0.0.0.0"       # Listen on all interfaces
PORT = 5001            # Must match the Arduino code
fs = 50                # Expected sampling rate (samples per second)
window_size_sec = 2    # Length of each sliding window in seconds
window_size = fs * window_size_sec  # e.g., 100 samples for a 2-second window
step_size = window_size // 2        # 50% overlap (e.g., 50 samples)
sensor_cols = ["Acce_x", "Acce_y", "Acce_z", "Gyro_x", "Gyro_y", "Gyro_z"]

# Load your pre-trained classification model
model = load("model/exercise_model.joblib")


# ---------------------------
# Create TCP Server
# ---------------------------
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print("Waiting for connection on port", PORT)

conn, addr = server_socket.accept()
print("Connected by", addr)

# Buffer for incoming sensor data
buffer = []

# ---------------------------
# Feature Extraction Function
# ---------------------------
def extract_features(window_df):
    features = {}
    for col in sensor_cols:
        # Ensure data are floats
        arr = window_df[col].values.astype(np.float64)
        features[f"{col}_mean"]   = np.mean(arr)
        features[f"{col}_std"]    = np.std(arr)
        features[f"{col}_min"]    = np.min(arr)
        features[f"{col}_max"]    = np.max(arr)
        features[f"{col}_energy"] = np.sum(np.square(arr)) / len(arr)
    return features

# ---------------------------
# Real-Time Classification Loop
# ---------------------------
print("Starting real-time classification. Perform your exercise and watch the predictions!")

while True:
    try:
        # Receive data from the device
        data = conn.recv(1024)
        if not data:
            break
        # Decode and split received data into lines
        lines = data.decode('utf-8').strip().splitlines()
        for line in lines:
            parts = line.split(',')
            if len(parts) >= 6:
                # Convert each part to float and form a data point
                data_point = {sensor_cols[i]: float(parts[i]) for i in range(6)}
                buffer.append(data_point)
    except Exception as e:
        print("Error processing data:", e)
    
    # Process if we have enough data for one window
    if len(buffer) >= window_size:
        window_df = pd.DataFrame(buffer[:window_size])
        feat = extract_features(window_df)
        feature_vector = np.array(list(feat.values())).reshape(1, -1)
        prediction = model.predict(feature_vector)[0]
        print("Real-time Prediction:", prediction)
        # Slide the window (50% overlap)
        buffer = buffer[step_size:]
    
    time.sleep(0.01)
