import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from joblib import dump
# -------------------------------
# 1. Load and Label the Data Files
# -------------------------------
# Update the filenames if necessary.
bicep = pd.read_csv("sensor_data_bicepcurl.csv", parse_dates=["Timestamp"])
bicep["Label"] = "BicepCurl"

overhead = pd.read_csv("sensor_data_overhead.csv", parse_dates=["Timestamp"])
overhead["Label"] = "OverHead"

pushup = pd.read_csv("sensor_data_pushup.csv", parse_dates=["Timestamp"])
pushup["Label"] = "PushUp"

# Combine the datasets
data = pd.concat([bicep, overhead, pushup], ignore_index=True)
data = data.sort_values("Timestamp").reset_index(drop=True)

# -------------------------------
# 2. Data Segmentation and Feature Extraction
# -------------------------------
# Assumptions:
# - The sensor files include these columns:
#   "Timestamp", "Acce_x", "Acce_y", "Acce_z", "Gyro_x", "Gyro_y", "Gyro_z"
# - The sampling rate is assumed to be 50 Hz (adjust if needed)
fs = 50                          # Sampling frequency (samples per second)
window_size_sec = 2              # Window duration in seconds
window_size = window_size_sec * fs  # Number of samples per window (e.g., 100)
step_size = window_size // 2        # 50% overlap (e.g., 50 samples)

# Helper function to safely convert a value to float.
def to_float(x):
    # If it's already a numeric type, return it as float.
    if isinstance(x, (int, float)):
        return float(x)
    try:
        # Remove any leading/trailing whitespace/newlines and split by whitespace.
        parts = str(x).strip().split()
        # Take the first token (or you could average all tokens if that makes sense)
        return float(parts[0])
    except Exception as e:
        print("Conversion error for value:", x, "Error:", e)
        return np.nan

def extract_features(window):
    features = {}
    sensor_cols = ["Acce_x", "Acce_y", "Acce_z", "Gyro_x", "Gyro_y", "Gyro_z"]
    for col in sensor_cols:
        # Convert each value in the column safely.
        arr = np.array([to_float(v) for v in window[col].values], dtype=np.float64)
        features[f"{col}_mean"]   = np.mean(arr)
        features[f"{col}_std"]    = np.std(arr)
        features[f"{col}_min"]    = np.min(arr)
        features[f"{col}_max"]    = np.max(arr)
        features[f"{col}_energy"] = np.sum(np.square(arr)) / len(arr)
    # Use Pandas mode to get the most common label in the window.
    features["Label"] = window["Label"].mode()[0]
    return features

features_list = []
num_samples = len(data)
for start in range(0, num_samples - window_size + 1, step_size):
    window = data.iloc[start : start + window_size]
    feat = extract_features(window)
    features_list.append(feat)

features_df = pd.DataFrame(features_list)
print("Extracted features shape:", features_df.shape)

# -------------------------------
# 3. Prepare Data for Classification
# -------------------------------
X = features_df.drop("Label", axis=1).values
y = features_df["Label"].values

# Split the data into training and testing sets.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.4, random_state=42
)

# -------------------------------
# 4. Train a Classifier and Evaluate
# -------------------------------
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Predict on the test set.
y_pred = clf.predict(X_test)

# Print classification metrics.
print("Classification Report:")
print(classification_report(y_test, y_pred))

# -------------------------------
dump(clf, 'exercise_model.joblib')
