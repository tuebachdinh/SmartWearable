# 🧤 Smart Gym Glove

A wearable system for automatic exercise classification using pressure sensors and motion data. Developed as part of the **ELEC-E7840 Smart Wearables** course at Aalto University, Spring 2025.

## 📌 Project Overview

The Smart Gym Glove helps users track their gym workouts by recognizing and classifying **8 upper-body exercises** in real-time using:

- Custom-made **PZR pressure sensors**
- An **ICM-20948 IMU (accelerometer + gyroscope)**
- **Machine learning models** running on a server

This eliminates the need for manual logging and supports users, especially beginners, in monitoring their fitness progress.

## 💡 Features

- 🔍 Real-time exercise classification (96% accuracy)
- 🧠 Random Forest model with custom feature extraction
- 📲 Wireless data transmission via Arduino MKR WiFi 1010
- 🧪 Tested with 5 users in real gym environments
- 🎥 Visual feedback + data logging
- 🧤 Comfortable, low-cost wearable design with DIY pressure sensors

## 🛠️ Hardware

- Arduino MKR WiFi 1010  
- ICM-20948 IMU  
- 5 custom laminated PZR pressure sensors  
- LiPo battery  
- Conductive thread and fabric  
- Stretchy base glove  
- **Cost**: ~10–20 EUR per glove (estimated for mass production)

## 🧬 Machine Learning

- **Model**: Random Forest Classifier  
- **Features**: IMU + pressure sensor data (mean, std, min, max, energy)  
- **Windowing**: 2-second sliding windows with 50% overlap  
- **Special Class**: "Undetected" if prediction confidence < 70%  
- **Accuracy**: 96% across 8 exercises

## 📊 Recognized Exercises

1. Bicep Curl  
2. Lateral Raise  
3. Wrist Curl  
4. Pull  
5. Overhead  
6. Plank  
7. Push-up  
8. Tricep Extension

## 👥 User Testing

- 5 subjects tested in gym settings
- Strong cross-subject generalization
- Positive feedback on comfort and usability
- Suggestions led to improved design and electronics attachment

## 🚀 Future Work

- Automatic repetition and set tracking  
- Real-time feedback and form correction  
- Better glove fit and sweat protection  
- Integration with mobile apps and cloud platforms  

## 🔗 Resources

- 📂 [Code Repository](https://github.com/tuebachdinh/SmartWearable)  
- 🎥 [Demo Video](https://drive.google.com/file/d/16nSSFtAXOe5_lulj8GwaVdIF1fUaZ842/view?usp=sharing)  
- 📋 [User Feedback Form](https://docs.google.com/forms/d/e/1FAIpQLSfvB7CHWwMLigTlAv8vrJtwsATprEbYW4zeWv4bxeDWPQdWvA/viewform)  
- 📈 [Survey Results](https://docs.google.com/spreadsheets/d/1oMZYGRMH2nKGzUj-7MaqrUk41iEWf0cLZyOA541Rz_g/edit?usp=sharing)
