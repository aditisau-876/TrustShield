def calculate_anomaly_score(data):

    score = 0

    # CPU abnormality
    if data["cpu_usage"] > 80:
        score += 20

    # Memory abnormality
    if data["memory_usage"] > 80:
        score += 15

    # Very high network traffic
    if data["packet_rate"] > 500:
        score += 25

    # Too many network connections
    if data["connections"] > 20:
        score += 20

    # Unusually high data transmission
    if data["data_sent_mb"] > 100:
        score += 10

    # Many failed commands
    if data["failed_commands"] > 5:
        score += 10

    return min(score, 100)


def classify_device(score):

    if score < 30:
        return "NORMAL"

    elif score < 60:
        return "SUSPICIOUS"

    elif score < 80:
        return "HIGH_RISK"

    else:
        return "CRITICAL"


# Test device
device = {
    "cpu_usage": 45,
    "memory_usage": 60,
    "packet_rate": 140,
    "connections": 3,
    "data_sent_mb": 15,
    "failed_commands": 0
}

score = calculate_anomaly_score(device)

print("Anomaly Score:", score)
print("Status:", classify_device(score))