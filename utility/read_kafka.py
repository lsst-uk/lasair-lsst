"""Read messages from the specified Kafka topic"""

import argparse
import string
from confluent_kafka import Consumer, KafkaError
from time import perf_counter, sleep
import uuid

def send(conf):
    kafka_conf = {
        'session.timeout.ms': 10000,
        'default.topic.config': {'auto.offset.reset': 'earliest'},
        'bootstrap.servers': conf['broker'],
        'client.id': 'client-1',
        'group.id': uuid.uuid4() # use a random group id
    }
    print("Group: ", kafka_conf['group.id'])
    c = Consumer(kafka_conf)
    c.subscribe([conf['topic']])
    sleep(4)
    start_t = perf_counter()
    n = 0
    e = 0
    while n < conf['n']:
        msg = c.poll(1)
        if msg is None:
            print(".")
            if e < 30:
                continue
            break
        elif not msg.error():
            n += 1
        else:
            print(str(msg.error()))
            break
    if n > 0:
        c.commit(asynchronous=False)
    end_t = perf_counter()
    c.close()
    tt = end_t - start_t
    print(f"Consumed {n} messages in {tt} s")

if __name__ == '__main__':
    # parse cmd line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-b', '--broker', default='localhost:9092', type=str, help='address:port of Kafka broker(s)')
    parser.add_argument('-n', type=int, default=1, help='number of messages to read')
    parser.add_argument('-t', '--topic', type=str, required=True, help='topic to read')
    conf = vars(parser.parse_args())

    send(conf)

