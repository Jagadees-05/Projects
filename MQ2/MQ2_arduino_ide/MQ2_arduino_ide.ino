#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// -------- WiFi Credentials --------
const char* ssid = "Airel_9842878776";
const char* password = "air88581";

// -------- MQTT Broker Details --------
const char* mqtt_server = "broker.emqx.io";  // You can use your broker IP
const int mqtt_port = 1883;
const char* mqtt_topic = "esp8266/mq2";

// -------- WiFi & MQTT Client --------
WiFiClient espClient;
PubSubClient client(espClient);

// -------- MQ2 Sensor Pin --------
#define MQ2_PIN A0

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
    if (client.connect("ESP8266Client12325423q")) {
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
  Serial.begin(115200);
  pinMode(MQ2_PIN, INPUT);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  int mq2_value = analogRead(MQ2_PIN); // Read MQ2 analog value
  Serial.print("MQ2 Sensor Value: ");
  Serial.println(mq2_value);

  char msg[10];
  dtostrf(mq2_value, 1, 2, msg); // Convert to string

  client.publish(mqtt_topic, msg); // Publish to MQTT
  delay(2000); // Send every 2 sec
}
