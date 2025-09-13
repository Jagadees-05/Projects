import paho.mqtt.client as mqtt
import mysql.connector
from datetime import datetime

# ---------- MQTT Details ----------
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "esp8266/mq2"

# ---------- MySQL Setup ----------
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASS = ""
DB_NAME = "works"
TABLE_NAME = "MQ2"



# ---------- Connect to MySQL ----------
db = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS
)
cursor = db.cursor()

# Create database if not exists
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
db.database = DB_NAME

# Create table if not exists
cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        sensor_value FLOAT,
        timestamp DATETIME
    )
""")
db.commit()

# ---------- MQTT Callbacks ----------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print("Failed to connect, return code %d\n", rc)



def on_message(client, userdata, msg):
    try:
        sensor_value = float(msg.payload.decode())
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(f"Received: {sensor_value} at {timestamp}")

        # Insert into MySQL
        sql = f"INSERT INTO {TABLE_NAME} (sensor_value, timestamp) VALUES (%s, %s)"
        val = (sensor_value, timestamp)
        cursor.execute(sql, val)
        db.commit()

    except Exception as e:
        print("Error:", e)

# ---------- Setup MQTT Client ----------
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

print("Listening for MQTT messages...")
client.loop_forever()
