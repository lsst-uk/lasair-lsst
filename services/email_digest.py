"""
For each filter with email output, checks the associated Kafka topic for new alerts,
builds a digest email and sends it. Intended to be run as a daily cronjob.
Usage:
    email_digest.py [--email=<address> --group=<id>] [--filter=<name>]

Options:
    --help             Show usage information
    --email=<address>  Send all alerts here instead of to users (for testing)
    --group=<id>       Group ID (for testing)
    --filter=<name>    Limit to a single filter (for testing)
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


def send_email(to_addr: str, fname: str, message: str, message_html: str = None, message_json: str = None):
    msg = MIMEMultipart('mixed')
    body = MIMEMultipart('alternative')

    msg['Subject'] = f"Lasair query {fname}"
    msg['From'] = settings.LASAIR_EMAIL
    msg['To'] = to_addr

    body.attach(MIMEText(message, 'plain'))
    if message_html:
        body.attach(MIMEText(message_html, 'html'))
    msg.attach(body)
    if message_json:
        attachment = MIMEApplication(message_json, 'json', Name=f"{fname}.json")
        attachment.add_header('Content-Disposition', 'attachment', filename=f"{fname}.json")
        msg.attach(attachment)
    s = smtplib.SMTP('localhost')
    s.sendmail('lasair@lsst.ac.uk', to_addr, msg.as_string())


def format_line(alert):
    text = ' '.join(str(value) for key, value in alert.items()) + "\n"
    html = "<tr>"
    for key, value in alert.items():
        if key == 'diaObjectId':
            html += f"<td><a href=\"https://{settings.LASAIR_URL}/objects/{str(value)}\">{str(value)}</a></td>"
        else:
            html += f"<td>{str(value)}</td>"
    html += "</tr>\n"
    return text, html


def format_message(fname, alerts):
    text = f"Lasair alert digest for filter {fname}\n\n"
    html = f"<html><head><title>Lasair alert digest for filter {fname}</title></head><body><table>\n"
    if len(alerts) > 0:
        text += ' | '.join(alerts[0].keys()) + "\n"
        html += "<tr>"
        for key in alerts[0]:
            html += f"<th>{key}</th>"
        html += "</tr>\n"
    for alert in alerts:
        line_text, line_html = format_line(alert)
        text += line_text
        html += line_html
    text += "\n"
    html += "</table></body></html>"
    return text, html


def main(to_addr, groupid, fname):
    if not groupid:
        groupid = 'email_digest'
    consumer_conf = {
        'bootstrap.servers': settings.PUBLIC_KAFKA_READONLY,
        'default.topic.config': {'auto.offset.reset': 'earliest'},
        'client.id': 'email_digest',
        'group.id': groupid,
        'enable.auto.commit': True,
    }

    # Get a list of filters
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = ("SELECT name, topic_name, first_name, last_name, email "
             "FROM myqueries, auth_user "
             "WHERE auth_user.id=user ")
    if fname:
        # get a specific query (for testing)
        query += f"AND myqueries.name='{fname}'"
    else:
        # get all email queries
        query += "AND output=%d" % OUTPUT_EMAIL
    cursor.execute(query)
    filters = cursor.fetchall()

    for f in filters:
        # Get any new alerts
        consumer = Consumer(consumer_conf)
        consumer.subscribe([f['topic_name']])
        alerts = []
        i = 0
        while i < 10:
            msg = consumer.poll(timeout=1)
            if msg is None:
                # no messages available
                i += 1
                sleep(1)
                continue
            if msg.error():
                print('ERROR polling for alerts: ' + str(msg.error()))
                break
            alerts.append(json.loads(msg.value()))
        consumer.close()

        # Create and send digest email
        if len(alerts) > 0:
            if not to_addr:
                to_addr = f['email']
            text, html = format_message(f['name'], alerts)
            json_str = json.dumps(alerts, indent=2)
            send_email(to_addr, f['name'], text, html, json_str)


if __name__ == "__main__":
    args = docopt(__doc__)
    email = args.get('--email')
    group = args.get('--group')
    filter_name = args.get('--filter')
    if email and not group or group and not email:
        print('Either both email and group options must be set, or neither.')
        sys.exit(1)
    main(email, group, filter_name)




