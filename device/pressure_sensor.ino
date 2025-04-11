// Define sensor pins
#define PALM_SENSOR_PIN A1
#define FINGER_SENSOR_PIN A2

// Define threshold values (adjust based on calibration)
const int lowThreshold   = 600;  // Below this value, sensor is considered "low"
const int moderateMin    = 700;  // Minimum for moderate pressure
const int moderateMax    = 950;  // Maximum for moderate pressure
const int highThreshold  = 960;  // Above this value, sensor is considered "high"

void setup() {
  Serial.begin(9600);
  // Optionally, initialize sensors or other hardware here
}

void loop() {
  // Read analog values from the sensors
  int palmValue = 1023 - analogRead(PALM_SENSOR_PIN);
  int fingerValue = 1023 - analogRead(FINGER_SENSOR_PIN);
  
  // Print raw sensor values for debugging
  // Print sensor values separated by a tab for the plotter
  Serial.print(palmValue);
  Serial.print("\t");
  Serial.println(fingerValue);
  
  // Determine grip type based on sensor thresholds
  if (palmValue > moderateMin && palmValue < moderateMax && fingerValue < lowThreshold) {
    Serial.println("Grip Detected: Open Grip");
  }
  else if ((palmValue >= moderateMin && palmValue <= moderateMax) &&
           (fingerValue >= moderateMin && fingerValue <= moderateMax)) {
    // Both sensors are in the moderate range → Closed Grip (thumb in)
    Serial.println("Grip Detected: Closed Grip");
  }
  else if (palmValue > highThreshold ) {
    // High pressure on palm, low on finger → Push Up (all palm down)
    Serial.println("Grip Detected: Push Up Palm Down");
  }
  else if (fingerValue > highThreshold) {
    // High pressure on finger, low on palm → Pinch Grip
    Serial.println("Grip Detected: Pinch Grip");
  }
  else {
    // If no condition is met, the grip is undefined or in transition.
    Serial.println("Grip Detected: Undefined / Transition");
  }
  
  // Small delay for sensor reading stability
  delay(500);
}
