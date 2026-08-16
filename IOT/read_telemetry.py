import json

with open("telemetry.json", "r") as file:
    data = json.load(file)

print(data)