"""
Make a Kafka topic non-expiring.
"""
import argparse
import json
from confluent_kafka.admin import AdminClient, ConfigResource, ConfigEntry, RESOURCE_TOPIC
from time import sleep

def get_config(conf):
    settings = {
        'bootstrap.servers': conf['broker'],
        }
    config = {}
    admin_client = AdminClient(settings)
    config_dict = { 'retention.ms': '-1' } 
    topic = ConfigResource(RESOURCE_TOPIC, conf['topic'], config_dict)
    #topic.add_incremental_config(ConfigEntry('retention.ms', 1))
    #future = admin_client.incremental_alter_configs([topic], validate_only=True)
    result_dict = admin_client.alter_configs([topic])
    result_dict[topic].result()
    sleep(0.2)

if __name__ == '__main__':
    # parse cmd line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-b', '--broker', type=str, default='localhost:9092', help='address:port of Kafka broker(s)')
    parser.add_argument('-t', '--topic', type=str, help='topic to change', required=True)
    conf = vars(parser.parse_args())

    get_config(conf)
