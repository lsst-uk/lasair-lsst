"""
Print a timestamp, total number of messages and message rate for a topic.
Repeat every second until interrupted.
"""

import argparse
from confluent_kafka import Consumer, TopicPartition, OFFSET_BEGINNING
import json
from time import sleep, perf_counter

def get_consumer(conf):
    kafka_conf = {
        'session.timeout.ms': 10000,
        'default.topic.config': {'auto.offset.reset': 'earliest'},
        'bootstrap.servers': conf['broker'],
        'client.id': 'client-1',
        'group.id': 'test-client'
    }
    return Consumer(kafka_conf)

def reset_offset(consumer, conf):
    parts = consumer.list_topics(topic=conf['topic']).topics[conf['topic']].partitions
    tps = []
    for p in parts:
        tp = TopicPartition(conf['topic'], p)
        tp.offset = OFFSET_BEGINNING
        tps.append(tp)
    consumer.assign(tps)


def get_count(conf):
    parts = consumer.list_topics(topic=conf['topic']).topics[conf['topic']].partitions
    total = 0
    for p in parts:
        offsets = consumer.get_watermark_offsets(TopicPartition(conf['topic'], p)) 
        total += offsets[1] - offsets[0]
    return total

if __name__ == '__main__':
    # parse cmd line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-b', '--broker', default='localhost:9092', type=str, help='address:port of Kafka broker(s)')
    parser.add_argument('-n', type=int, default=1, help='number of messages to read')
    parser.add_argument('-t', '--topic', type=str, required=True, help='topic to read')
    conf = vars(parser.parse_args())

    consumer = get_consumer(conf)
    start = perf_counter()
    prev_time = 0
    prev_total = get_count(conf)
    while True:
        sleep(1)
        now = perf_counter() - start
        total = get_count(conf)
        rate = (total - prev_total) / (now - prev_time)
        print (f"{now:.3f} {total} {rate}")
        prev_time = now
        prev_total = total
