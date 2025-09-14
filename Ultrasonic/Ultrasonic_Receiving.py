import paho.mqtt.client as mqtt
import mysql.connector
from datetime import datetime
from twilio.rest import Client

# ---------- MQTT Details ----------
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "esp8266/ultrasonic"

# ---------- MySQL Setup ----------
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASS = ""
DB_NAME = "works"
TABLE_NAME = "ultrasonic"

# ---------- Twilio Setup ----------
TWILIO_SID = "YOUR_ACCOUNT_SID"
TWILIO_AUTH_TOKEN = "YOUR_AUTH_TOKEN"
TWILIO_NUMBER = "+1234567890"   # Twilio number
TO_NUMBER = "+91XXXXXXXXXX"     # Your number
THRESHOLD = 10                   # Distance in cm (alert if object closer than this)

twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

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
        id INT AUTO_INCREMENT PRIMARY KEY,
        distance FLOAT,
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

def send_twilio_alert(value, timestamp):
    message = f"ALERT! Ultrasonic distance low: {value} cm at {timestamp}"
    try:
        twilio_client.messages.create(
            body=message,
            from_=TWILIO_NUMBER,
            to=TO_NUMBER
        )
        print("Twilio alert sent!")
    except Exception as e:
        print("Twilio Error:", e)

def on_message(client, userdata, msg):
    try:
        distance = float(msg.payload.decode())
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(f"Distance: {distance} cm at {timestamp}")

        # Insert into MySQL
        sql = f"INSERT INTO {TABLE_NAME} (distance, timestamp) VALUES (%s, %s)"
        val = (distance, timestamp)
        cursor.execute(sql, val)
        db.commit()

        # Send Twilio alert if distance below threshold
        if distance <= THRESHOLD:
            send_twilio_alert(distance, timestamp)

    except Exception as e:
        print("Error:", e)

# ---------- Setup MQTT Client ----------
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
print("Listening for Ultrasonic sensor messages...")
client.loop_forever()
