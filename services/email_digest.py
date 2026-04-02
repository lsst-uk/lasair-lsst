"""
For each filter with email output, checks the associated Kafka topic for new alerts,
builds a digest email and sends it. Intended to be run as a daily cronjob.
Usage:
    email_digest.py

Options:
    --help     Show usage information
"""

import sys
sys.path.append('../common')
from docopt import docopt
from src import db_connect
from confluent_kafka import Consumer
import settings


args = docopt(__doc__)

consumer_conf = {
    'bootstrap.servers': '',
    'default.topic.config': {'auto.offset.reset': 'earliest'},
    'client.id': 'client-1',
    'group.id': '',
    'enable.auto.commit': False,
}

msl = db_connect.remote()
cursor = msl.cursor(buffered=True, dictionary=True)
query = f"SELECT topic_name, first_name, last_name, email FROM myqueries, auth_user WHERE auth_user.id=user AND active=1"
cursor.execute(query)
for row in cursor:
    print(row)

