import base64

with open("weather-station-460903-b0b8c0a316c2.json", "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

print(encoded)
