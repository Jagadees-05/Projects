import json
import paho.mqtt.client as mqtt
import mysql.connector

# ---------- MySQL Setup ----------
db = mysql.connector.connect(
    host="localhost",
    user="root",        # change if you set another username
    password="",        # add your MySQL root password if set
    database="works"
)

cursor = db.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS IR_Sensor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor VARCHAR(50),
    value INT,
    status VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
db.commit()

# ---------- MQTT Setup ----------
BROKER = "broker.emqx.io"   # same as ESP8266 code
PORT = 1883
TOPIC = "esp8266/ir"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(TOPIC)
    else:
        print("Failed to connect, return code:", rc)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print("Received:", data)

        sensor = data.get("sensor", "IR")
        value = int(data.get("value", 0))
        status = data.get("status", "Unknown")

        cursor.execute("INSERT INTO IR_Sensor (sensor, value, status) VALUES (%s, %s, %s)", 
                       (sensor, value, status))
        db.commit()
        print("Data inserted into MySQL!")

    except Exception as e:
        print("Error:", e)

# ---------- Main ----------
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
print("Listening for messages...")

client.loop_forever()
