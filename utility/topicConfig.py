"""
Get the configuration parameters for a Kafka topic.
"""
import argparse
import json
from confluent_kafka.admin import AdminClient, ConfigResource, RESOURCE_TOPIC
from time import sleep

def get_config(conf):
    settings = {
        'bootstrap.servers': conf['broker'],
        }
    config = {}
    admin_client = AdminClient(settings)
    topic = ConfigResource(RESOURCE_TOPIC, conf['topic'])
    result = admin_client.describe_configs([topic])[topic].result()
    for k,v in result.items():
        config[k] = v.value
    print(json.dumps(config, indent=2))
    sleep(0.2)

if __name__ == '__main__':
    # parse cmd line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-b', '--broker', type=str, default='localhost:9092', help='address:port of Kafka broker(s)')
    parser.add_argument('-t', '--topic', type=str, help='topic to inspect', required=True)
    conf = vars(parser.parse_args())

    get_config(conf)
