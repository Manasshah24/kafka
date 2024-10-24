#!/usr/bin/env python3

from flask import Flask, request, jsonify
from kafka import KafkaProducer
from kafka import KafkaConsumer
import json

TOPIC_REGISTER = "register"
TOPIC_TEST_CONFIG = "test_config"
TOPIC_TRIGGER = "trigger"
TOPIC_METRICS = "metrics"
TOPIC_HEARTBEAT = "heartbeat"


producer = KafkaProducer(bootstrap_servers='localhost:9092')
# consumer = KafkaConsumer(
#     bootstrap_servers='localhost:9092', 
#     group_id='orchestrator')

app = Flask(__name__)

test_count = 0

@app.route('/tsunami')
def tsunami_test():
    global test_count

    delay = request.args.get('delay', 0)
    messages_per_driver = request.args.get('messages_per_driver', 0)
    test_count += 1

    test_config = {
        "test_id": 'TSUNAMI_' + str(test_count),
        "test_type": "TSUNAMI",
        "test_message_delay": delay,
        "message_count_per_driver": messages_per_driver
    }
    producer.send(TOPIC_TEST_CONFIG, json.dumps(test_config).encode('utf8'))

    with open("driver_nodes.json","r") as f:
        nodes = json.load(f)

    return test_config['test_id']

@app.route('/avalanche')
def avalanche_test():
    global test_count

    messages_per_driver = request.args.get('messages_per_driver', 0)
    test_count += 1

    test_config = {
        "test_id": 'AVALANCHE_' + str(test_count),
        "test_type": "AVALANCHE",
        "test_message_delay": 0,
        "message_count_per_driver": messages_per_driver
    }
    producer.send(TOPIC_TEST_CONFIG, json.dumps(test_config).encode('utf8'))

    with open("driver_nodes.json","r") as f:
        nodes = json.load(f)

    return test_config['test_id']

@app.get('/get_metrics')
def get_metrics():
    metric_data = {}
    with open('metric_data.json','r') as f:
        metric_data = json.load(f)

    return jsonify(metric_data), 200

@app.get('/get_metrics/<test_id>')
def get_test_data(test_id):
    metric_data = {}
    with open('metric_data.json','r') as f:
        metric_data = json.load(f)

    return jsonify(metric_data[test_id]), 200


@app.get('/get_nodes')
def get_nodes_data():
    metric_data = {}
    with open('driver_nodes.json','r') as f:
        metric_data = json.load(f)

    return jsonify(metric_data), 200

if __name__ == '__main__':  
     app.run()