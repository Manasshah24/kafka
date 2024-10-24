#!/usr/bin/env python3

from kafka import KafkaProducer
from kafka import KafkaConsumer
import json
import sys
import datetime
import threading
from time import sleep

TOPIC_REGISTER = "register"
TOPIC_TEST_CONFIG = "test_config"
TOPIC_TRIGGER = "trigger"
TOPIC_METRICS = "metrics"
TOPIC_HEARTBEAT = "heartbeat"

producer = KafkaProducer(bootstrap_servers='localhost:9092')
consumer = KafkaConsumer(
    TOPIC_REGISTER, 
    TOPIC_TEST_CONFIG, 
    TOPIC_METRICS,
    TOPIC_HEARTBEAT, 
    bootstrap_servers='localhost:9092', 
    group_id='orchestrator')

nodes = {}

def register_node(node):
    global nodes
    nodes[node['node_id']] = {
        "node_id": node['node_id'],
        "node_IP": node['node_IP'],
        "status": "UP",
        "last_updated": str(datetime.datetime.now())
    }
    json_object = json.dumps(nodes, indent=4)
    with open("driver_nodes.json", "w") as outfile:
        outfile.write(json_object)

def heartbeat(hb):
    global nodes
    if hb['node_id'] in nodes.keys():
        nodes[hb['node_id']]['last_updated'] = hb['timestamp']
        json_object = json.dumps(nodes, indent=4)
        with open("driver_nodes.json", "w") as outfile:
            outfile.write(json_object)

def update_driver_status():
    global nodes
    while True:
        if nodes:
            for node_id, node in nodes.items():
                # last_updated = datetime.datetime.strptime(node['last_updated'], '%Y-%m-%d %H:%M:%S')
                last_updated = datetime.datetime.fromtimestamp(node['last_updated'])
                difference = datetime.datetime.now() - last_updated
                if difference >= datetime.timedelta(seconds=5) and nodes[node_id]['status'] == 'UP':
                    nodes[node_id]['status'] = 'DOWN'
                    json_object = json.dumps(nodes, indent=4)
                    with open("driver_nodes.json", "w") as outfile:
                        outfile.write(json_object)
        sleep(30)

def metric_update(metrics):
    metric_data = {}
    with open('metric_data.json','r') as f:
        metric_data = json.load(f)
    print(metric_data)
    if metrics['test_id'] not in metric_data.keys():
        metric_data[metrics['test_id']] = {metrics['node_id']: metrics['metrics']}
    else:
        metric_data[metrics['test_id']][metrics['node_id']] = metrics['metrics']

    json_object = json.dumps(metric_data, indent=4)
    with open("metric_data.json", "w") as outfile:
        outfile.write(json_object)

def kafka_consume_messages():
    for message in consumer:
        topic = message.topic
        value = json.loads(message.value.decode('utf-8'))
        if topic == TOPIC_REGISTER:
            print({'register': value})
            register_node(value)
        elif topic == TOPIC_METRICS:
            print({'metric': value})
            metric_update(value)
        elif topic == TOPIC_TEST_CONFIG:
            print({'test_config': value})
            trigger = {
                "test_id": value['test_id'],
                "trigger": "YES"
            }
            producer.send(TOPIC_TRIGGER, json.dumps(trigger).encode('utf8'))
        elif topic == TOPIC_HEARTBEAT:
            print({'heartbeat': value})
            heartbeat(value)

if __name__ == '__main__':
    t1 = threading.Thread(target=kafka_consume_messages)
    t2 = threading.Thread(target=update_driver_status)

    t1.start()
    t2.start()
