"""
Check that annotations are working as expected
    Make active annotator
    if filtactive: Make filter that uses it
    Make annotation and post it in via API
    Check its there
    if active > 0: wait until filter has run
    if active > 1: check email/Kafka message is produced
    if active > 0: Delete the filter
    Delete the annotator and its annotations

Usage:
    check_annotation.py --topic=<topic> --annactive=[no|yes|fast] --filtactive=[no|email|kafka] --user=<user> --token=<token>

Options:
    --topic: throwaway topic name for annotator that will be made/destroyed
    --annactive=<annaction>: (no|yes|fast) action attribute for the annotator
        no: the annotation will not be accepted by Lasair (action=0)
        yes: annotation will be accepted (action=1)
        fast: annotation will be accepted and cause filters to run (action=2)
    --filtactive=[email|kafka]: Filter that runs against the annotator
        no:    inactive filter will be made
        email: will be sent to user from the filter
        kafka: will be produced with topic name
    --user=<user>: user name for annotator owner
    --token=<token>: API token for that user
"""
import sys, docopt
import lasair
sys.path.append('../common')
import settings
from src import db_connect, topic_name

def get_user_id(msl, username):
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'SELECT id FROM auth_user WHERE username="%s"' % username
    cursor.execute(query)
    for row in cursor:
        return row['id']
    return None

def get_diaObjectId(msl):
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'SELECT diaObjectId FROM objects LIMIT 1'
    cursor.execute(query)
    for row in cursor:
        return row['diaObjectId']
    return None

def make_annotator(msl, topic, username, active, user_id):
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'INSERT INTO annotators (topic, username, active, public, user) '
    query += 'VALUES ("%s", "%s", %d, %d, %d)'
    query = query % (topic, username, active, 0, user_id)
    cursor.execute(query)
    msl.commit()

def delete_annotator(msl, topic):
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'DELETE FROM annotators WHERE topic="%s"' % topic
    cursor.execute(query)
    msl.commit()

def make_annotation(L, topic, diaObjectId):
    classdict      = {'fruit': 'apple'}
    classification = 'ripe'
    explanation    = 'another nice apple'
    L.annotate(
        topic,
        diaObjectId,
        classification,
        version='0.1',
        explanation=explanation,
        classdict=classdict,
        url='')

def kafka_consumer(filter_topic, server='lasair-lsst-dev-kafka:9092'):
    group_id = 'hello%04d' % random.randrange(10000)
    consumer = lasair.lasair_consumer(server, group_id, filter_topic)
    return consumer

def make_filter(msl, topic, active, user_id):
    user_id = get_user_id(msl, username)
    cursor = msl.cursor(buffered=True, dictionary=True)

    public = 0
    filter_name = topic+'_filter'
    selected = 'objects.diaObjectId'
    conditions = ''
    tables = "objects, annotator:%s" % topic
    filter_topic = topic_name.topic_name(user_id, filter_name)

    real_sql = "SELECT objects.diaObjectId FROM objects,annotations AS %s "
    real_sql += "WHERE objects.diaObjectId=%s.diaObjectId AND %s.topic='%s' "
    real_sql = real_sql % (topic, topic, topic, topic)

    query = 'INSERT INTO myqueries '
    query += '(name, selected, conditions, tables, public, active, topic_name, real_sql, user) '
    query += 'VALUES ("%s", "%s", "%s", "%s", %d, %d, "%s", "%s", %d)'
    query = query % (filter_name, selected, conditions, tables, public, active, filter_topic, real_sql, user_id)
    print(query)
#    cursor.execute(query)
    msl.commit()

def delete_filter(msl, topic):
    filter_name = topic+'_filter'
    print('deleting filter with name=%s' % filter_name)
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'DELETE FROM myqueries WHERE name="%s"' % filter_name
    cursor.execute(query)
    msl.commit()


if __name__ == "__main__":
    args = docopt.docopt(__doc__)
    print(args)
    topic    = args['--topic']
    username = args['--user']
    if args['--annactive'] == 'no':   annactive = 0
    if args['--annactive'] == 'yes':  annactive = 1
    if args['--annactive'] == 'fast': annactive = 2

    if args['--filtactive'] == 'no'   : filtactive = 0
    if args['--filtactive'] == 'email': filtactive = 1
    if args['--filtactive'] == 'kafka': filtactive = 2

    L = lasair.lasair_client(args['--token'], endpoint='https://lasair-lsst-dev.lsst.ac.uk/api')
    ra = 61.893163
    dec = -30.001845
#    c = L.cone(ra, dec, radius=240.0, requestType='all')
#    print(c)

    msl = db_connect.remote()
    user_id = get_user_id(msl, username)
    print('using user_id = %s' % str(user_id))
    diaObjectId = get_diaObjectId(msl)
    print('using diaObjectId=%s' % str(diaObjectId))

    make_annotator(msl, topic, args['--user'], annactive, user_id)
    make_filter(msl, topic, filtactive, user_id)
    make_annotation(L, topic, diaObjectId)

#    delete_filter(msl, topic)
#    delete_annotator(msl, topic)
