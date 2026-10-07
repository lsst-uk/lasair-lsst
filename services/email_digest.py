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
from src import annotate_util, db_connect, date_nid, slack_webhook
from src.send_email import send_email
from confluent_kafka import Consumer
import settings
from time import sleep
import json
from datetime import datetime

logfile = ''
logf = sys.stdout

# marks_for_objects IS SPECIFIED AGAINST A CAPPED RESULT TABLE; A DIGEST TOPIC IS NOT
MARK_LOOKUP_CHUNK = 1000


def format_line(alert):
    text = ' '.join(str(value) for key, value in alert.items()) + "\n"
    html = "<tr>"
    for key, value in alert.items():
        if key.lower() == 'diaobjectid':
            html += f"<td><a href=\"https://{settings.LASAIR_URL}/objects/{str(value)}\">{str(value)}</a></td>"
        else:
            html += f"<td>{str(value)}</td>"
    html += "</tr>\n"
    return text, html


def alert_object_id(alert):
    """The diaObjectId of one digest message, matched case-insensitively as
    format_line already does, or None when the message carries no id."""
    for key, value in alert.items():
        if key.lower() == 'diaobjectid':
            return value
    return None


def suppress_hidden(alerts, topic):
    """Remove the recipient's hidden objects from a filter's digest messages.

    Applied to every email filter with no branch on how the filter runs. For an
    annotation-triggered filter it costs one query and removes nothing, which
    is the price of not carrying a second mode — and it still buys something
    the SQL cannot, because the digest runs up to twenty-four hours after the
    messages were produced, so an object hidden in that window is suppressed.

    A message with no diaObjectId passes through: there is nothing to match on,
    and dropping rows on a guess would be worse. That is a known hole.

    Args:
        alerts: the messages polled from the filter's topic
        topic: the recipient's tag topic, `tags_<username>`

    Returns:
        `(kept, omitted)` — the messages to send, and how many were removed
    """
    if not alerts:
        return [], 0

    diaObjectIds = [oid for oid in (alert_object_id(a) for a in alerts) if oid is not None]

    hidden = set()
    for start in range(0, len(diaObjectIds), MARK_LOOKUP_CHUNK):
        chunk = diaObjectIds[start:start + MARK_LOOKUP_CHUNK]
        marks = annotate_util.marks_for_objects(topic, chunk)
        hidden.update(oid for oid, mark in marks.items() if mark == annotate_util.MARK_HIDDEN)

    kept = [a for a in alerts if alert_object_id(a) not in hidden]
    return kept, len(alerts) - len(kept)


def format_message(fname, alerts, omitted=0):
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
    html += "</table>"
    if omitted:
        note = f"{omitted} hidden objects omitted"
        text += note + "\n"
        html += f"<p>{note}</p>"
    html += "</body></html>"
    return text, html


def main(to_addr, groupid, fname):
    now = datetime.now()
    logf.write(f'Starting email_digest at {now}\n') 
    if not groupid:
        groupid = 'email_digest_1352'
    consumer_conf = {
        'bootstrap.servers': settings.PUBLIC_KAFKA_READONLY,
        'default.topic.config': {'auto.offset.reset': 'earliest'},
        'client.id': 'email_digest',
        'group.id': groupid,
        'enable.auto.commit': False,
    }

    # Get a list of filters
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = ("SELECT name, topic_name, first_name, last_name, email, username "
             "FROM myqueries, auth_user "
             "WHERE auth_user.id=user ")
    params = []
    if fname:
        # get a specific query (for testing)
        query += "AND myqueries.name=%s"
        params.append(fname)
    else:
        # get all email queries
        query += "AND output=%s"
        params.append(settings.OUTPUT_EMAIL)
    cursor.execute(query, tuple(params))
    filters = cursor.fetchall()

    consumer = Consumer(consumer_conf)

    for f in filters:
        # Get any new alerts
        consumer.subscribe([f['topic_name']])
        sleep(2)
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

        polled = len(alerts)

        # The second pass: hidden objects never reach the filter's Kafka topic,
        # so they are removed here
        omitted = 0
        try:
            alerts, omitted = suppress_hidden(alerts, annotate_util.tag_topic(f['username']))
        except Exception as e:
            logf.write('ERROR reading marks for %s: %s\n' % (f['username'], str(e)))

        # Create and send digest email
        if len(alerts) > 0:
            # The --email test override must not be overwritten by the real address
            recipient = to_addr if to_addr else f['email']
            text, html = format_message(f['name'], alerts, omitted=omitted)
            json_str = json.dumps(alerts, indent=2)
            logf.write('%d from topic %s\n' % (len(alerts), f['topic_name']))
            if len(json_str) < 3000000:
                send_email(recipient, f['name'], text, html, json_str)
            else:
                logf.write('ERROR: message too large to send as email')
        else:
            logf.write('No new output in topic %s\n' % (f['topic_name']))

        # Committing rides on having polled, not on having sent. Otherwise a
        # digest whose every message was hidden is re-polled and re-dropped
        # every night for ever.
        if polled > 0:
            try:
                consumer.commit(asynchronous=False)
                sleep(2)
            except Exception as e:
                logf.write('ERROR: ' + str(e))

        consumer.unsubscribe()
        sleep(2)
    consumer.close()


if __name__ == "__main__":
    args = docopt(__doc__)
    email = args.get('--email')
    group = args.get('--group')
    service_log = args.get('--log')

    nid = date_nid.nid_now()
    date = date_nid.nid_to_date(nid)
    if service_log:
        logfile = settings.SERVICES_LOG + '/' + date + '.log'
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




