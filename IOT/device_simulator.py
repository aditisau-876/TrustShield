import json
import random
import time
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883

DEVICE_ID = "CAMERA_01"

client = mqtt.Client()

client.connect(BROKER, PORT, 60)

print("CAMERA_01 connected to MQTT broker")

while True:

    telemetry = {
        "device_id": DEVICE_ID,
        "device_type": "CCTV",

        "cpu_usage": random.randint(30, 60),
        "memory_usage": random.randint(40, 70),

        "packet_rate": random.randint(80, 150),
        "connections": random.randint(2, 5),

        "data_sent_mb": random.randint(5, 20),
        "data_received_mb": random.randint(5, 15),

        "failed_commands": random.randint(0, 1)
    }

    message = json.dumps(telemetry)

    client.publish("devicetrust/telemetry", message)

    print("Sent:", telemetry)

    time.sleep(3)