#include <Wire.h>
#include <Adafruit_ICM20X.h>
#include <SPI.h>
#include <WiFiNINA.h> // Or WiFi101, depending on your board

/***** Wi-Fi Credentials *****/
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

/***** Server Details *****/
const char* serverIP   = "192.168.1.100";  // Replace with your computer's local IP
const int   serverPort = 5001;            // Must match the Python server script

/***** Create ICM-20948 Object *****/
Adafruit_ICM20948 icm;

/***** Wi-Fi Client *****/
WiFiClient client;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  // 1) Initialize I2C
  Wire.begin();

  // 2) Initialize the ICM-20948 sensor over I2C
  if (!icm.begin_I2C()) {
    Serial.println("Failed to find ICM-20948 chip");
    while (1) { delay(10); }
  }
  Serial.println("ICM-20948 Found!");

  // (Optional) Configure sensor ranges & sample rates
  // icm.setAccelRange(ICM20X_ACCEL_RANGE_2_G);
  // icm.setGyroRange(ICM20X_GYRO_RANGE_250_DPS);
  // icm.setSampleRateDiv(5);  // Adjust internal data rate if desired

  // 3) Connect to Wi-Fi
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  while (WiFi.begin(ssid, password) != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("\nConnected to WiFi!");

  // 4) Connect to the Python server
  Serial.print("Connecting to server...");
  while (!client.connect(serverIP, serverPort)) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("\nConnected to server!");
}

void loop() {
  if (client.connected()) {
    // Create sensor event objects
    sensors_event_t accel, gyro, temp, mag;
    icm.getEvent(&accel, &gyro, &temp, &mag);

    // Prepare CSV-like data string: Acce_x, Acce_y, Acce_z, Gyro_x, Gyro_y, Gyro_z
    // If you only need accelerometer, you can omit gyro/mag.
    String dataString = "";
    dataString += String(accel.acceleration.x) + ",";
    dataString += String(accel.acceleration.y) + ",";
    dataString += String(accel.acceleration.z) + ",";
    dataString += String(gyro.gyro.x) + ",";
    dataString += String(gyro.gyro.y) + ",";
    dataString += String(gyro.gyro.z) + ",";
    // dataString += String(mag.magnetic.x) + ",";
    // dataString += String(mag.magnetic.y) + ",";
    // dataString += String(mag.magnetic.z);

    // Send data to the server
    client.println(dataString);
    Serial.println("Sent: " + dataString);

    // ~50Hz sampling (20ms delay)
    delay(20);
  } else {
    // Attempt to reconnect if disconnected
    Serial.println("Disconnected, trying to reconnect...");
    client.stop();
    delay(2000);
    client.connect(serverIP, serverPort);
  }
}
