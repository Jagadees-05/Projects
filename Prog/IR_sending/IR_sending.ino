#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ---------- WiFi Credentials ----------
const char* ssid = "Poi recharge Pannu da karuvaya";
const char* password = "fathima ali";

// ---------- MQTT Broker ----------
const char* mqtt_server = "broker.emqx.io";   // or your broker IP
const int mqtt_port = 1883;
const char* mqtt_topic = "esp8266/ir";

// ---------- IR Sensor Pin ----------
#define IR_SENSOR_PIN D5  // GPIO14

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266Clientjdshgyaev")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  pinMode(IR_SENSOR_PIN, INPUT);
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  int irValue = digitalRead(IR_SENSOR_PIN);

  // Create JSON
  StaticJsonDocument<200> doc;
  doc["value"] = irValue;
  doc["status"] = (irValue == LOW) ? "Object detected" : " No object detected";

  char buffer[256];
  size_t n = serializeJson(doc, buffer);

  // Publish to MQTT
  client.publish(mqtt_topic, buffer, n);

  Serial.print("Published: ");
  Serial.println(buffer);

  delay(2000); // send every 2 seconds
}
