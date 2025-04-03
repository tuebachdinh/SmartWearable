#include <Wire.h>
#include <Adafruit_ICM20948.h>  // Use the ICM20948-specific header
#include <SPI.h>
#include <WiFiNINA.h>           // Or WiFi101, depending on your board
#define PALM_SENSOR_PIN A5
#define FINGER1_SENSOR_PIN A1
#define FINGER2_SENSOR_PIN A2
#define FINGER3_SENSOR_PIN A3
#define FINGER4_SENSOR_PIN A4

// Define threshold values (adjust based on calibration)
const int lowThreshold   = 600;  // Below this value, sensor is considered "low"
const int moderateMin    = 600;  // Minimum for moderate pressure
const int moderateMax    = 950;  // Maximum for moderate pressure
const int highThreshold  = 960;  // Above this value, sensor is considered "high"

/***** Wi-Fi Credentials *****/
const char* ssid     = "aalto open";
const char* password = "";

/***** Server Details *****/
const char* serverIP   = "192.168.10.58";  // Replace with your computer's local IP
const int   serverPort = 5001;             // Must match the Python server script

Adafruit_ICM20948 icm;
WiFiClient client;

bool sendData = true; // Flag to control data transmission

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  // Initialize I2C
  Wire.begin();

  // Initialize the ICM-20948 sensor over I2C
  if (!icm.begin_I2C()) {
    Serial.println("Failed to find ICM-20948 chip");
    while (1) { delay(10); }
  }
  Serial.println("ICM-20948 Found!");

  // Connect to Wi-Fi
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  while (WiFi.begin(ssid, password) != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("\nConnected to WiFi!");

  // Connect to the Python server
  Serial.print("Connecting to server...");
  while (!client.connect(serverIP, serverPort)) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("\nConnected to server!");
  
  Serial.println("Type 's' to stop data transmission, 'r' to resume.");
}

void loop() {
  // Check for Serial commands to control transmission
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 's') {
      sendData = false;
      Serial.println("Data transmission stopped.");
    } else if (command == 'r') {
      sendData = true;
      Serial.println("Data transmission resumed.");
    }
  }
  
  if (sendData && client.connected()) {
    // Create sensor event objects
    sensors_event_t accel, gyro, temp, mag;
    icm.getEvent(&accel, &gyro, &temp, &mag);

    int palmValue = 1023 - analogRead(PALM_SENSOR_PIN);
    int fingerValue1 = 1023 - analogRead(FINGER1_SENSOR_PIN);
    int fingerValue2 = 1023 - analogRead(FINGER2_SENSOR_PIN);
    int fingerValue3 = 1023 - analogRead(FINGER3_SENSOR_PIN);
    int fingerValue4 = 1023 - analogRead(FINGER4_SENSOR_PIN);
    int fingerValue = (fingerValue1 + fingerValue2 + fingerValue3 + fingerValue4)/4
    String gridType;
    Serial.print(palmValue);
    Serial.print("\t");
    Serial.println(fingerValue);
    
    // Determine grip type based on sensor thresholds
    if (palmValue > moderateMin && palmValue < moderateMax && fingerValue < lowThreshold) {
      gridType = "Open Grip";
    }
    else if ((palmValue >= moderateMin && palmValue <= moderateMax) && (fingerValue >= moderateMin && fingerValue <= moderateMax)) { 
      // Both sensors are in the moderate range → Closed Grip (thumb in)
      gridType = "Closed Grip";
    }
    else if (palmValue > highThreshold ) { // High pressure on palm, low on finger → Push Up (all palm down)
      gridType = "Palm Down";
    }
    else if (fingerValue > highThreshold) {. // High pressure on finger, low on palm → Pinch Grip
      gridType = "Pinch Grip";
    }
    else {// If no condition is met, the grip is undefined or in transition.
      gridType = "Undetected";
    }
    Serial.println("Grip Type: " + gridType);
    // Prepare CSV-like data string: Acce_x, Acce_y, Acce_z, Gyro_x, Gyro_y, Gyro_z
    String dataString = "";
    dataString += String(accel.acceleration.x) + ",";
    dataString += String(accel.acceleration.y) + ",";
    dataString += String(accel.acceleration.z) + ",";
    dataString += String(gyro.gyro.x) + ",";
    dataString += String(gyro.gyro.y) + ",";
    dataString += String(gyro.gyro.z);
    dataString += gridType;


    // Send data to the server
    client.println(dataString);
    Serial.println("Sent: " + dataString);

    // ~50Hz sampling (20ms delay)
    delay(20);
  } else if (!client.connected()) {
    // Attempt to reconnect if disconnected
    Serial.println("Disconnected, trying to reconnect...");
    client.stop();
    delay(2000);
    client.connect(serverIP, serverPort);
  }
}
