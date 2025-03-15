import time
import serial
import pandas as pd
import numpy as np
from joblib import load

# ---------------------------
# Parameters & Setup
# ---------------------------
# Sliding window parameters (adjust as needed)
fs = 50                          # Expected sampling frequency (samples per second)
window_size_sec = 2              # Window length in seconds
window_size = fs * window_size_sec  # e.g., 100 samples for 2 seconds at 50Hz
step_size = window_size // 2         # 50% overlap

# Sensor column names (order should match data sent from Arduino)
sensor_cols = ["Acce_x", "Acce_y", "Acce_z", "Gyro_x", "Gyro_y", "Gyro_z"]

# Load your pre-trained model (ensure this file exists)
model = load("exercise_model.joblib")

# Setup the serial connection
# Update the serial port name and baud rate according to your system
ser = serial.Serial('/dev/tty.usbmodemXYZ', 115200, timeout=1)
print("Serial connection established.")

# Buffer to store incoming sensor data
buffer = []

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
# Real-Time Classification Loop
# ---------------------------
print("Starting real-time classification. Perform your exercise and see the result!")
while True:
    # Read a line from serial (non-blocking)
    if ser.in_waiting:
        try:
            line = ser.readline().decode('utf-8').strip()
            # Expected format: "Acce_x,Acce_y,Acce_z,Gyro_x,Gyro_y,Gyro_z"
            parts = line.split(',')
            if len(parts) >= 6:
                # Convert each part to float and create a dictionary
                data_point = {sensor_cols[i]: float(parts[i]) for i in range(6)}
                buffer.append(data_point)
        except Exception as e:
            print("Error reading line:", e)
    
    # If we've collected enough samples for one window, process them
    if len(buffer) >= window_size:
        # Create a DataFrame from the first window_size samples
        window_df = pd.DataFrame(buffer[:window_size])
        # Extract features
        feat = extract_features(window_df)
        # Convert features to array (order must match training)
        feature_vector = np.array(list(feat.values())).reshape(1, -1)
        # Predict the exercise class
        prediction = model.predict(feature_vector)[0]
        print("Predicted Exercise:", prediction)
        # Slide the window: remove step_size samples from the buffer
        buffer = buffer[step_size:]
    
    # A short sleep to avoid busy waiting
    time.sleep(0.01)
