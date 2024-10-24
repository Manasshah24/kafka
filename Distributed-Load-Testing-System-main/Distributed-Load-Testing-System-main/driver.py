#!/usr/bin/env python3

from kafka import KafkaProducer
from kafka import KafkaConsumer
import json
import sys
import os
import socket
import requests
from time import sleep
from statistics import mean, median
import datetime
import threading

TOPIC_REGISTER = "register"
TOPIC_TEST_CONFIG = "test_config"
TOPIC_TRIGGER = "trigger"
TOPIC_METRICS = "metrics"
TOPIC_HEARTBEAT = "heartbeat"

KAFKA_IP, ORCHESTRATOR_IP, TARGET_URL = sys.argv[1], sys.argv[2], sys.argv[3]

HOSTNAME = socket.gethostname()
IP_ADDR = socket.gethostbyname(HOSTNAME)
PID = os.getpid()

DRIVER_ID = HOSTNAME + "_" + str(PID)

tests = {}

producer = KafkaProducer(bootstrap_servers=KAFKA_IP + ':9092')
consumer = KafkaConsumer(
    TOPIC_TEST_CONFIG,
    TOPIC_TRIGGER,
    bootstrap_servers=KAFKA_IP + ':9092',
    group_id=DRIVER_ID)

def store_test(test):
    global tests
    tests[test['test_id']] = test

def tsunami_test(test):
    global TARGET_URL, DRIVER_ID
    test_times = []
    min_latency = 0
    max_latency = 0
    for i in range(int(test['message_count_per_driver'])):
        time_elapsed = requests.get(TARGET_URL).elapsed.total_seconds()*1000
        test_times.append(time_elapsed)
        if time_elapsed > max_latency:
            max_latency = time_elapsed
        if time_elapsed < min_latency or min_latency == 0:
            min_latency = time_elapsed
        message = {
            "node_id": DRIVER_ID,
            "test_id": test['test_id'],
            "report_id": test['test_id'] + "_" + DRIVER_ID + "_" + str(i),
            "metrics": {
                "mean_latency": mean(test_times),
                "median_latency": median(test_times),
                "min_latency": min_latency,
                "max_latency": max_latency
            }
        }
        producer.send(TOPIC_METRICS, json.dumps(message).encode('utf8'))
        sleep(float(test['test_message_delay']))
    del tests[test['test_id']]

def avalanche_test(test):
    global TARGET_URL
    test_times = []
    min_latency = 0
    max_latency = 0
    for i in range(int(test['message_count_per_driver'])):
        time_elapsed = requests.get(TARGET_URL).elapsed.total_seconds()*1000
        test_times.append(time_elapsed)
        if time_elapsed > max_latency:
            max_latency = time_elapsed
        if time_elapsed < min_latency or min_latency == 0:
            min_latency = time_elapsed
        message = {
            "node_id": DRIVER_ID,
            "test_id": test['test_id'],
            "report_id": test['test_id'] + "_" + DRIVER_ID + "_" + str(i),
            "metrics": {
                "mean_latency": mean(test_times),
                "median_latency": median(test_times),
                "min_latency": min_latency,
                "max_latency": max_latency
            }
        }
        producer.send(TOPIC_METRICS, json.dumps(message).encode('utf8'))
    del tests[test['test_id']]

def trigger_test(test_id):
    global tests
    test = tests[test_id]
    if test['test_type'] == 'TSUNAMI':
        tsunami_test(test)
    elif test['test_type'] == 'AVALANCHE':
        avalanche_test(test)
    
def heartbeat():
    global DRIVER_ID
    heartbeat = {
        "node_id": DRIVER_ID,
        "heartbeat": "YES"
    }
    while True:
        ct = datetime.datetime.now()
        heartbeat['timestamp'] = ct.timestamp()
        producer.send(TOPIC_HEARTBEAT, json.dumps(heartbeat).encode('utf8'))
        sleep(3)

def kafka_consume_messages():
    for message in consumer:
        topic = message.topic
        value = json.loads(message.value.decode('utf-8'))

        if topic == TOPIC_TEST_CONFIG:
            store_test(value)
        elif topic == TOPIC_TRIGGER:
            print({'trigger': value})
            if value['trigger'] == 'YES':
                trigger_test(value['test_id'])

if __name__ == '__main__':
    register = {
      "node_id": DRIVER_ID,
      "node_IP": IP_ADDR,
      "message_type": "DRIVER_NODE_REGISTER"
    }
    producer.send(TOPIC_REGISTER, json.dumps(register).encode('utf-8'))

    t1 = threading.Thread(target=heartbeat)
    t2 = threading.Thread(target=kafka_consume_messages)

    t1.start()
    t2.start()