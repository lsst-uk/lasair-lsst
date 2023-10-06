"""Send random messages of the specified size to Kafka"""

import argparse
import string
from random import choices
from confluent_kafka import Producer, KafkaError

def send(conf):
    kafka_conf = {
        'bootstrap.servers': conf['broker'],
        'client.id': 'client-1',
    }
    p = Producer(kafka_conf)
    for i in range(conf['n']):
        msg = ''.join(choices(string.ascii_letters, k=conf['s']))
        p.produce(conf['topic'], msg)
    p.flush()

if __name__ == '__main__':
    # parse cmd line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-b', '--broker', default='localhost:9092', type=str, help='address:port of Kafka broker(s)')
    parser.add_argument('-n', type=int, default=1, help='number of messages to send')
    parser.add_argument('-s', type=int, default=10, help='size of messages to send in bytes')
    parser.add_argument('-t', '--topic', type=str, required=True, help='topic to send to')
    conf = vars(parser.parse_args())

    send(conf)

