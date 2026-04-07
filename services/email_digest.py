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
from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import json


consumer_conf = {
    'bootstrap.servers': settings.PUBLIC_KAFKA_READONLY,
    'default.topic.config': {'auto.offset.reset': 'earliest'},
    'client.id': 'email_digest',
    'group.id': 'email_digest',
    'enable.auto.commit': True,
}


def send_email(to_addr: str, subject: str, message: str, message_html: str = None, message_json: str = None):
    msg = MIMEMultipart('alternative')

    msg['Subject'] = subject
    msg['From'] = settings.LASAIR_EMAIL
    msg['To'] = to_addr

    msg.attach(MIMEText(message, 'plain'))
    if message_html:
        msg.attach(MIMEText(message_html, 'html'))
    if message_json:
        msg.attach(MIMEApplication(message_json, 'json'))
    s = smtplib.SMTP('localhost')
    s.sendmail('lasair@lsst.ac.uk', to_addr, msg.as_string())


def format_line(alert):
    text = ' '.join(str(value) for key, value in alert.items()) + "\n"
    html = "<tr>"
    for key, value in alert.items():
        if key == 'objectId':
            html += f"<td><a href=\"https://{settings.LASAIR_URL}/objects/{str(value)}\">{str(value)}</a></td>"
        else:
            html += str(value)
    html += "</tr>\n"
    return text, html


def format_message(fname, alerts):
    text = f"Lasair alert digest for filter {fname}\n\n"
    html = f"<html><head><title>Lasair alert digest for filter {fname}</title></head><body><table>\n"
    for alert in alerts:
        line_text, line_html = format_line(alert)
        text += line_text
        html += line_html
    text += "\n"
    html += "</table></body></html>"
    return text, html


def main():
    # Get a list of filters
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = ("SELECT name, topic_name, first_name, last_name, email"
             "FROM myqueries, auth_user"
             "WHERE auth_user.id=user AND active=1")
    cursor.execute(query)
    filters = cursor.items()

    for f in filters:
        # Get any new alerts
        consumer = Consumer(consumer_conf)
        consumer.subscribe([f['topic_name']])
        alerts = []
        for i in range(10):
            msg = consumer.poll(timeout=1)
            if msg is None:
                # no messages available
                sleep(1)
                continue
            if msg.error():
                print('ERROR polling for alerts: ' + str(msg.error()))
                break
            alerts.append(json.loads(msg.value()))
        consumer.close()

        # Create and send digest email
        if len(alerts) > 0:
            text, html = format_message(f['name'], alerts)
            json_str = json.dumps(alerts, indent=2)
            send_email(f['email'], f"Lasair query {f['name']}", text, html, json_str)


if __name__ == "__main__":
    args = docopt(__doc__)
    main()




