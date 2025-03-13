import pandas as pd
import numpy as np
from scipy.stats import mode
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# -----------------------------
# 1. Data Preprocessing
# -----------------------------
# Load the labeled CSV file. Adjust the filename as necessary.
data = pd.read_csv("sensor_data_labeled.csv", parse_dates=["Timestamp"])

# Assume the CSV has at least these columns: 
# "Timestamp", "Acce_x", "Acce_y", "Acce_z", "Gyro_x", "Gyro_y", "Gyro_z", "Label"
# Drop any rows where Label is missing.
data = data.dropna(subset=["Label"])
data = data.sort_values("Timestamp").reset_index(drop=True)

# (Optional) You may add additional cleaning steps if needed.

# -----------------------------
# 2. Data Segmentation (Windowing)
# -----------------------------
# Assuming a sampling rate of 50 Hz, choose a window length and step.
fs = 50                      # Sampling frequency: 50 samples per second
window_size_sec = 2          # Window duration in seconds (e.g., 2 sec)
window_size = window_size_sec * fs  # Number of samples per window (e.g., 100)
step_size = window_size // 2         # 50% overlap (e.g., 50 samples)

# Function to extract features from a window of data.
def extract_features(window):
    features = {}
    sensor_channels = ["Acce_x", "Acce_y", "Acce_z", "Gyro_x", "Gyro_y", "Gyro_z"]
    for channel in sensor_channels:
        data_channel = window[channel].values
        # Statistical features: mean, std, min, max, and energy
        features[f"{channel}_mean"]   = np.mean(data_channel)
        features[f"{channel}_std"]    = np.std(data_channel)
        features[f"{channel}_min"]    = np.min(data_channel)
        features[f"{channel}_max"]    = np.max(data_channel)
        features[f"{channel}_energy"] = np.sum(np.square(data_channel)) / len(data_channel)
    
    # Label the window using the majority label within the window
    labels = window["Label"].values
    features["label"] = mode(labels)[0][0]
    return features

# Slide a window through the data and extract features.
features_list = []
num_samples = len(data)
for start in range(0, num_samples - window_size + 1, step_size):
    window = data.iloc[start:start + window_size]
    feat = extract_features(window)
    features_list.append(feat)

# Create a DataFrame containing all extracted features.
features_df = pd.DataFrame(features_list)
print("Extracted feature shape:", features_df.shape)

# -----------------------------
# 3. Prepare Data for Model Training
# -----------------------------
# Separate features (X) and labels (y)
X = features_df.drop("label", axis=1).values
y = features_df["label"].values

# Split the dataset into training and testing sets.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# -----------------------------
# 4. Model Training and Evaluation
# -----------------------------
# Create and train a Random Forest classifier.
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Predict labels for the test set.
y_pred = clf.predict(X_test)

# Evaluate the model.
print("Classification Report:")
print(classification_report(y_test, y_pred))
