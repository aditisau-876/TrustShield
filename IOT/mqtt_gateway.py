import json
import paho.mqtt.client as mqtt

from anomaly_detector import calculate_anomaly_score, classify_device


BROKER = "localhost"
PORT = 1883
TOPIC = "devicetrust/telemetry"


def on_connect(client, userdata, flags, rc):

    print("Connected to MQTT broker")

    client.subscribe(TOPIC)

    print("Subscribed to:", TOPIC)


def on_message(client, userdata, msg):

    data = json.loads(msg.payload.decode())

    # Calculate anomaly score
    score = calculate_anomaly_score(data)

    # Classify device
    status = classify_device(score)

    print("\n========== DEVICE TRUST ==========")

    print("Device:", data["device_id"])
    print("Type:", data["device_type"])

    print("CPU:", data["cpu_usage"])
    print("Memory:", data["memory_usage"])
    print("Packet Rate:", data["packet_rate"])
    print("Connections:", data["connections"])
    print("Data Sent:", data["data_sent_mb"])
    print("Data Received:", data["data_received_mb"])
    print("Failed Commands:", data["failed_commands"])

    print("----------------------------------")

    print("Anomaly Score:", score)
    print("Device Status:", status)

    print("==================================")


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)

client.loop_forever()