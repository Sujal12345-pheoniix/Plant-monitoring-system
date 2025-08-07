#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Web server
WebServer server(80);

// Serial communication with Arduino Uno
#define ARDUINO_RX 16  // ESP32 RX pin connected to Arduino TX
#define ARDUINO_TX 17  // ESP32 TX pin connected to Arduino RX

// Variables to store sensor data
float moistureLevel = 0;

void setup() {
  // Initialize Serial for debugging
  Serial.begin(115200);
  
  // Initialize Serial1 for communication with Arduino
  Serial1.begin(9600, SERIAL_8N1, ARDUINO_RX, ARDUINO_TX);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  // Setup API endpoints
  server.on("/", handleRoot);
  server.on("/moisture", handleMoisture);
  server.on("/pump", handlePump);
  
  server.begin();
}

void loop() {
  server.handleClient();
  
  // Read data from Arduino Uno
  if (Serial1.available()) {
    String data = Serial1.readStringUntil('\n');
    data.trim();
    
    if (data.startsWith("moisture:")) {
      moistureLevel = data.substring(9).toFloat();
    }
  }
}

void handleRoot() {
  String html = "<html><body>";
  html += "<h1>Plant Monitoring System</h1>";
  html += "<p>Soil Moisture: " + String(moistureLevel) + "%</p>";
  html += "<button onclick=\"fetch('/pump?state=on')\">Turn Pump On</button>";
  html += "<button onclick=\"fetch('/pump?state=off')\">Turn Pump Off</button>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handleMoisture() {
  StaticJsonDocument<200> doc;
  doc["moisture"] = moistureLevel;
  
  String response;
  serializeJson(doc, response);
  
  server.send(200, "application/json", response);
}

void handlePump() {
  if (server.hasArg("state")) {
    String state = server.arg("state");
    if (state == "on") {
      Serial1.println("pump:on");
      server.send(200, "text/plain", "Pump turned ON");
    } else if (state == "off") {
      Serial1.println("pump:off");
      server.send(200, "text/plain", "Pump turned OFF");
    } else {
      server.send(400, "text/plain", "Invalid state");
    }
  } else {
    server.send(400, "text/plain", "Missing state parameter");
  }
} 