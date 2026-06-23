"""
For each filter with email output, checks the associated Kafka topic for new alerts,
builds a digest email and sends it. Intended to be run as a daily cronjob.
Usage:
    email_digest.py [--email=<address> --group=<id>] [--filter=<name>] [--log]

Options:
    --help             Show usage information
    --email=<address>  Send all alerts here instead of to users (for testing)
    --group=<id>       Group ID (for testing)
    --filter=<name>    Limit to a single filter (for testing)
    --log              If present, logs to service log
"""

import sys
sys.path.append('../common')
from docopt import docopt
from src import db_connect, date_nid, slack_webhook
from src.send_email import send_email
from confluent_kafka import Consumer
import settings
from time import sleep
import json
from datetime import datetime

logfile = ''
logf = sys.stdout


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
    now = datetime.now()
    logf.write(f'Starting email_digest at {now}\n') 
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
        query += "AND output=%d" % settings.OUTPUT_EMAIL
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
                logf.write('ERROR polling for alerts: ' + str(msg.error()))
                break
            alerts.append(json.loads(msg.value()))
        consumer.commit()
        consumer.close()

        # Create and send digest email
        if len(alerts) > 0:
            to_addr = f['email']
            topic = f['topic_name']
            text, html = format_message(f['name'], alerts)
            json_str = json.dumps(alerts, indent=2)
            logf.write('%d from topic %s\n' % (len(alerts), topic))
            send_email(to_addr, f['name'], text, html, json_str)


if __name__ == "__main__":
    args = docopt(__doc__)
    email = args.get('--email')
    group = args.get('--group')
    service_log = args.get('--log')

    nid  = date_nid.nid_now()
    date = date_nid.nid_to_date(nid)
    if service_log:
        logfile = settings.SERVICES_LOG + '/'+ date + '.log'
        try:
            logf = open(logfile, 'a')
        except Exception as e:
            s = "ERROR %s" % str(e)
            slack_channel = getattr(settings, 'SLACK_CHANNEL', None)
            slack_webhook.send(settings.SLACK_URL, s, channel=slack_channel)
            sys.exit(1)

    filter_name = args.get('--filter')
    if email and not group or group and not email:
        print('Either both email and group options must be set, or neither.')
        sys.exit(1)
    main(email, group, filter_name)




