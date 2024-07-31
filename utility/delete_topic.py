"""
Delete a Kafka topic.
"""
import argparse
import json
from confluent_kafka.admin import AdminClient
import time

def delete_topic(topic):
    settings = {
        'bootstrap.servers': conf['broker'],
        }
    admin_client = AdminClient(settings)
    result_dict = admin_client.delete_topics([topic])
    result_dict[topic].result()
    time.sleep(0.5)

if __name__ == '__main__':
    # parse cmd line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-b', '--broker', type=str, default='localhost:9092', help='address:port of Kafka broker(s)')
    parser.add_argument('-t', '--topic', type=str, help='topic to delete', required=True)
    conf = vars(parser.parse_args())

    delete_topic(conf['topic'])

