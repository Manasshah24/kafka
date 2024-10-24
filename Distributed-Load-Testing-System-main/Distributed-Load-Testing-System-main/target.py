from flask import Flask, jsonify
from prometheus_client import Histogram, generate_latest, REGISTRY

app = Flask('app')

# Initialize Monitoring
histogram = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

# Ping Endpoint
@app.route("/ping")
def ping():
    print("pong")
    return jsonify(message="pong"), 200

# Metrics Endpoint
@app.route("/metrics")
def metrics():
    return generate_latest(REGISTRY), 200, {"Content-Type": "text/plain"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

