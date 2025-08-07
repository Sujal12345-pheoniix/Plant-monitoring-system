// Pin definitions
const int MOISTURE_SENSOR_PIN = A0;  // Soil moisture sensor
const int RELAY_PIN = 3;             // Relay module for water pump

// Sensor calibration values
const int DRY_VALUE = 1023;  // Value when sensor is dry
const int WET_VALUE = 0;     // Value when sensor is wet

// Variables to store sensor readings
float moistureLevel = 0;

void setup() {
  Serial.begin(9600);
  
  // Initialize pins
  pinMode(MOISTURE_SENSOR_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  
  // Initialize relay (HIGH means pump is OFF)
  digitalWrite(RELAY_PIN, HIGH);
}

void loop() {
  // Read moisture sensor
  readMoisture();
  
  // Send sensor data
  sendSensorData();
  
  // Check for incoming commands
  if (Serial.available() > 0) {
    handleCommand();
  }
  
  delay(1000);  // Wait for 1 second
}

void readMoisture() {
  // Read moisture sensor
  int rawMoisture = analogRead(MOISTURE_SENSOR_PIN);
  moistureLevel = map(rawMoisture, DRY_VALUE, WET_VALUE, 0, 100);
}

void sendSensorData() {
  // Send data in format: "moisture:XX"
  Serial.print("moisture:");
  Serial.println(moistureLevel);
}

void handleCommand() {
  String command = Serial.readStringUntil('\n');
  command.trim();
  
  if (command == "pump:on") {
    controlPump(true);
  } else if (command == "pump:off") {
    controlPump(false);
  }
}

void controlPump(bool state) {
  // Relay is active LOW, so we invert the state
  digitalWrite(RELAY_PIN, !state);
} 