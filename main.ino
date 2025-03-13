#include <Wire.h>
#include <Adafruit_ICM20X.h>

// Create an ICM-20948 object
Adafruit_ICM20948 icm;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  // Initialize I2C
  Wire.begin();

  // Try to initialize the ICM-20948
  if (!icm.begin_I2C()) {
    Serial.println("Failed to find ICM-20948 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("ICM-20948 Found!");

  // Optional: Set full-scale ranges, low-pass filters, etc.
  // icm.setAccelRange(ICM20X_ACCEL_RANGE_2_G); // ±2g, ±4g, ±8g, ±16g
  // icm.setGyroRange(ICM20X_GYRO_RANGE_250_DPS); 
  // ...etc.

  // Optional: Configure sample rate
  // icm.setSampleRateDiv(10); // Adjust to set output data rate

  // Optional: Enable the magnetometer
  // icm.enableDMP(true); // For advanced features, e.g., built-in sensor fusion
}

void loop() {
  // Create sensor event objects
  sensors_event_t accel;
  sensors_event_t gyro;
  sensors_event_t temp;
  sensors_event_t mag; 

  // Read all the sensor data
  icm.getEvent(&accel, &gyro, &temp, &mag);

  // Print accelerometer readings
  Serial.print("Accel X: ");
  Serial.print(accel.acceleration.x);
  Serial.print(" m/s^2, Y: ");
  Serial.print(accel.acceleration.y);
  Serial.print(" m/s^2, Z: ");
  Serial.print(accel.acceleration.z);
  Serial.println(" m/s^2");

  // (Optional) Print gyro, mag, temp if desired
  // Serial.print("Gyro X: ");
  // Serial.print(gyro.gyro.x);
  // ...
  // Serial.print("Mag X: ");
  // ...
  // Serial.print("Temperature: ");
  // ...

  // Delay for readability (adjust as needed)
  delay(500);
}
