#include <ArduinoJson.h>

// Pin definitions
const int MOISTURE_SENSOR_PIN = A0;
const int TEMPERATURE_SENSOR_PIN = A1;
const int LIGHT_SENSOR_PIN = A2;
const int WATER_PUMP_PIN = 3;
const int LED_PIN = 4;

// Sensor calibration values
const int DRY_VALUE = 1023;  // Value when sensor is dry
const int WET_VALUE = 0;     // Value when sensor is wet

// Variables to store sensor readings
float moistureLevel = 0;
float temperature = 0;
float lightLevel = 0;

void setup() {
  Serial.begin(9600);
  
  // Initialize pins
  pinMode(MOISTURE_SENSOR_PIN, INPUT);
  pinMode(TEMPERATURE_SENSOR_PIN, INPUT);
  pinMode(LIGHT_SENSOR_PIN, INPUT);
  pinMode(WATER_PUMP_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // Initialize actuators
  digitalWrite(WATER_PUMP_PIN, LOW);
  digitalWrite(LED_PIN, LOW);
}

void loop() {
  // Read sensors
  readSensors();
  
  // Send sensor data
  sendSensorData();
  
  // Check for incoming commands
  if (Serial.available() > 0) {
    handleCommand();
  }
  
  delay(1000);  // Wait for 1 second
}

void readSensors() {
  // Read moisture sensor
  int rawMoisture = analogRead(MOISTURE_SENSOR_PIN);
  moistureLevel = map(rawMoisture, DRY_VALUE, WET_VALUE, 0, 100);
  
  // Read temperature sensor (example using LM35)
  int rawTemp = analogRead(TEMPERATURE_SENSOR_PIN);
  temperature = (rawTemp * 5.0 / 1024.0) * 100.0;
  
  // Read light sensor
  lightLevel = map(analogRead(LIGHT_SENSOR_PIN), 0, 1023, 0, 100);
}

void sendSensorData() {
  StaticJsonDocument<200> doc;
  
  doc["moisture"] = moistureLevel;
  doc["temperature"] = temperature;
  doc["light"] = lightLevel;
  
  serializeJson(doc, Serial);
  Serial.println();
}

void handleCommand() {
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, Serial);
  
  if (error) {
    Serial.println("Error parsing JSON");
    return;
  }
  
  String action = doc["action"];
  float value = doc["value"];
  
  if (action == "water") {
    controlWaterPump(value);
  } else if (action == "light") {
    controlLight(value);
  }
}

void controlWaterPump(float duration) {
  digitalWrite(WATER_PUMP_PIN, HIGH);
  delay(duration * 1000);  // Convert seconds to milliseconds
  digitalWrite(WATER_PUMP_PIN, LOW);
}

void controlLight(float intensity) {
  analogWrite(LED_PIN, map(intensity, 0, 100, 0, 255));
} 