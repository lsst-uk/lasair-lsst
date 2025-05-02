"""Copy messages between the specified Kafka topic"""

import argparse
import string
from confluent_kafka import Consumer, Producer, KafkaError
from time import perf_counter, sleep
import uuid


def copy(conf):
    consumer_conf = {
        'session.timeout.ms': 10000,
        'default.topic.config': {'auto.offset.reset': 'earliest'},
        'bootstrap.servers': conf['src_broker'],
        'client.id': 'client-1',
        'group.id': uuid.uuid4() # use a random group id
    }
    producer_conf = {
        'bootstrap.servers': conf['dest_broker'],
        'client.id': 'client-1',
    }
    #print("Group: ", kafka_conf['group.id'])
    p = Producer(producer_conf)
    c = Consumer(consumer_conf)
    c.subscribe([conf['in_topic']])
    sleep(4)
    start_t = perf_counter()
    n = 0
    e = 0
    while n < conf['n']:
        msg = c.poll(1)
        if msg is None:
            print(".", end='')
            if e < 30:
                e += 1
                continue
            break
        elif not msg.error():
            p.produce(conf['out_topic'], msg.value())
            n += 1
        else:
            print(str(msg.error()))
            break
        if n % 10 == 0:
            p.flush()
    if n > 0:
        try:
            p.flush()
            c.commit(asynchronous=False)
        except:
            pass
    end_t = perf_counter()
    c.close()
    tt = end_t - start_t
    print(f"Copied {n} messages in {tt} s")


if __name__ == '__main__':
    # parse cmd line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-b', '--src_broker', default='localhost:9092', type=str, help='address:port of Kafka broker(s)')
    parser.add_argument('-d', '--dest_broker', default='localhost:9092', type=str, help='address:port of Kafka broker(s)')
    parser.add_argument('-n', type=int, default=1, help='number of messages to copy')
    parser.add_argument('-i', '--in_topic', type=str, required=True, help='topic to read')
    parser.add_argument('-o', '--out_topic', type=str, required=True, help='topic to write')
    conf = vars(parser.parse_args())

    copy(conf)


