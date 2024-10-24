# Distributed Load Testing System

## About the Project
### Architecture
![Architecture Diagram Not Loading](image.png)

### Technologies used
- :snake: Python
- :twisted_rightwards_arrows: Kafka
- :hot_pepper: Flask
- :crown: Streamlit
- :panda_face: Pandas

> Go would be the ideal choice for implementation, which was informed to us beforehand, but python was used as the team was familiar with it and we'd have to learn Go from scratch and then implement this, which wouldn't be possible in the 4 hours we thought we had anyway.

> Messages are passed around withing the file system as .json files for convinience.

### Testing Results
- :weight_lifting: Handles upto 12000 requests concurrently
- :zap: Average Response time of 120ms

## Running it
> Use on Linux Only!!

open up 4 terminal instances
1. run kafka and zookeeper
2. run kafka-client
```
python3 kafka-client.py
```
3. run orchestrator  
```
python3 orchestrator.py
```
4. run target.py
```
python3 target.py
```
5. run as many drivers as required
for each, open a terminal and run 
```
python3 driver.py KAFKA_IP, ORCHESTRATOR_IP, TARGET_URL
```
> Driver code takes command line arguments for `KAFKA_IP, ORCHESTRATOR_IP, TARGET_URL` respectively
6. run streamlit frontend
```
streamlit run frontend.py
```

Now you can choose between `tsunami` and `avalanche` tests and then perform the test and view metrics

### About the Tests
- tsunami_test:
    - Repeatedly sends GET requests.
    - Records the time taken for each request.
    - Calculates mean, median, min, and max latencies.
    - Sends the metrics to a Kafka topic after each request.
    - Waits for a specified delay between requests.

- avalanche_test:
    - Similar to tsunami_test but without the delay between requests.
    - Sends the metrics to a Kafka topic after each request.

Test configuration is deleted after completion for both.
