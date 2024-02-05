"""
Check that annotations are working as expected
You will need a username and its API token
Choose a topic name that is not the same as an existong annotator
If you choose annactive=yes: then the filter should work as expected -- something about fruit
If you choose annactive=fast, the filter works as before BUT ALSO
    if the filtactive is email, you should get an email
    if the filtactive is kafka, you should see result in public kafka
Note that no alerts are sent here, so the filter will not respond to them.

Usage:
    check_annotation.py --topic=<topic> --annactive=[no|yes|fast] --filtactive=[no|email|kafka] --user=<user> --token=<token>

Options:
    --topic: throwaway topic name for annotator that will be made/destroyed
    --annactive=<annaction>: (no|yes|fast) action attribute for the annotator
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
    query = 'SELECT id,email FROM auth_user WHERE username="%s"' % username
    cursor.execute(query)
    for row in cursor:
        return (row['id'], row['email'])
    return (None,None) 

def get_diaObjectId(msl):
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'SELECT diaObjectId FROM objects LIMIT 1'
    cursor.execute(query)
    for row in cursor:
        return row['diaObjectId']
    return None

def make_annotator(msl, topic, username, annactive, user_id):
    print('Making annotator with topic %s (%s)' % (topic, annactive))
    if annactive  == 'yes'  : active = 1
    if annactive  == 'fast' : active = 2
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'INSERT INTO annotators (topic, username, active, public, user) '
    query += 'VALUES ("%s", "%s", %d, %d, %d)'
    query = query % (topic, username, active, 0, user_id)
    cursor.execute(query)
    msl.commit()

def delete_annotator(msl, topic):
    print('Deleting annotator with topic=%s' % topic)
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'DELETE FROM annotators WHERE topic="%s"' % topic
    cursor.execute(query)
    msl.commit()

def make_annotation(L, topic, diaObjectId):
    print('Making annotation for topic %s, diaObjectId %s' % (topic, str(diaObjectId)))
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

def kafka_consumer(filter_topic):
    server = settings.PUBLIC_KAFKA_SERVER
    group_id = 'hello%04d' % random.randrange(10000)
    consumer = lasair.lasair_consumer(server, group_id, filter_topic)
    return consumer

def make_filter(msl, topic, filtactive, user_id):
    print('Making filter for annotation %s (%s)' % (topic, filtactive))
    if filtactive == 'no'   : active = 0
    if filtactive == 'email': active = 1
    if filtactive == 'kafka': active = 2

    (user_id, email) = get_user_id(msl, username)
    cursor = msl.cursor(buffered=True, dictionary=True)

    public = 0
    filter_name = topic+'_filter'
    selected = 'objects.diaObjectId'
    conditions = ''
    tables = "objects, annotator:%s" % topic
    filter_topic = topic_name.topic_name(user_id, filter_name)
    print('Using filter topic ', filter_topic)

    real_sql = "SELECT objects.diaObjectId FROM objects,annotations AS %s "
    real_sql += "WHERE objects.diaObjectId=%s.diaObjectId AND %s.topic='%s' "
    real_sql = real_sql % (topic, topic, topic, topic)

    query = 'INSERT INTO myqueries '
    query += '(name, selected, conditions, tables, public, active, topic_name, real_sql, user) '
    query += 'VALUES ("%s", "%s", "%s", "%s", %d, %d, "%s", "%s", %d)'
    query = query % (filter_name, selected, conditions, tables, public, active, filter_topic, real_sql, user_id)
    cursor.execute(query)
    msl.commit()
    return filter_topic

def run_filter(L, annotator_name):
    print('Running filter on annotator %s' % annotator_name)
    selected    = 'objects.diaObjectId, %s.classification, %s.classdict'
    selected = selected % (annotator_name, annotator_name)
    tables      = 'objects, annotator:%s' % annotator_name
    conditions  = ''
    c = L.query(selected, tables, conditions, limit=10)
    return c

def delete_filter(msl, topic):
    filter_name = topic+'_filter'
    print('Deleting filter with name=%s' % filter_name)
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'DELETE FROM myqueries WHERE name="%s"' % filter_name
    cursor.execute(query)
    msl.commit()


if __name__ == "__main__":
    args = docopt.docopt(__doc__)
#    print(args)
    topic    = args['--topic']
    username = args['--user']

    L = lasair.lasair_client(args['--token'], \
            endpoint='https://lasair-lsst-dev.lsst.ac.uk/api')
#    ra = 61.893163
#    dec = -30.001845
#    c = L.cone(ra, dec, radius=240.0, requestType='all')
#    print(c)

    msl = db_connect.remote()

    (user_id, email) = get_user_id(msl, username)
    print('using user_id = %s' % str(user_id))

    diaObjectId = get_diaObjectId(msl)
    print('using diaObjectId=%s' % str(diaObjectId))

    make_annotator(msl, topic, args['--user'], args['--annactive'], user_id)
    filter_topic = make_filter   (msl, topic, args['--filtactive'], user_id)
    make_annotation(L, topic, diaObjectId)

    result = run_filter(L, topic)
    print('Result is:', result)

    if args['--annactive']  == 'fast' :
        if args['--filtactive'] == 'email':
            print('Check your email ', email)
        if args['--filtactive'] == 'kafka':
            print('Check public kafka %s, topic %s' %\
                (settings.PUBLIC_KAFKA_SERVER, filter_topic))

    delete_filter(msl, topic)
    delete_annotator(msl, topic)
