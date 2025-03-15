#include <Wire.h>
#include <Adafruit_ICM20948.h>  // Use the ICM20948-specific header
#include <SPI.h>
#include <WiFiNINA.h>           // Or WiFi101, depending on your board

/***** Wi-Fi Credentials *****/
const char* ssid     = "yuuu";
const char* password = "servin022";

/***** Server Details *****/
const char* serverIP   = "192.168.10.58";  // Replace with your computer's local IP
const int   serverPort = 5001;             // Must match the Python server script

/***** Create ICM-20948 Object *****/
Adafruit_ICM20948 icm;

/***** Wi-Fi Client *****/
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

    // Prepare CSV-like data string: Acce_x, Acce_y, Acce_z, Gyro_x, Gyro_y, Gyro_z
    String dataString = "";
    dataString += String(accel.acceleration.x) + ",";
    dataString += String(accel.acceleration.y) + ",";
    dataString += String(accel.acceleration.z) + ",";
    dataString += String(gyro.gyro.x) + ",";
    dataString += String(gyro.gyro.y) + ",";
    dataString += String(gyro.gyro.z);
    // Optionally, include magnetometer data if needed:
    // dataString += "," + String(mag.magnetic.x) + "," + String(mag.magnetic.y) + "," + String(mag.magnetic.z);

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
