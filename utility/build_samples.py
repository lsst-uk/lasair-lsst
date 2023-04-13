"""
Build Samples
Create and display the sample records and TNS watchlist needed to bootstrap Lasair
"""

import sys
sys.path.append('../common')
from src import db_connect

sys.path.append('../webserver/lasair')
from query_builder import check_query, build_query

def get_id_for_username(username):
    """ Get the user_id for a given username
    """
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'SELECT id FROM auth_user WHERE username="%s"' % username
    cursor.execute(query)
    for row in cursor:
        return(row['id'])

def create_TNS(user_id, radius):
    """ Build a watchlist where the TNS can go
    Once it is populated, this will fail dues to FK constraint
    """
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'REPLACE INTO watchlists (wl_id, name, description, active, public, radius, user)'
    query += ' VALUES (1, "__TNS__", "Copy of Transient Name Server", 1, 0, %f, %d)'
    query = query % (radius, user_id)
    cursor.execute(query)
    msl.commit()

def create_lightweight_query(user_id):
    """ The Lightweight query pushes every alert out by Kafka
    Can be used to monitor operation of public kafka and filter nodes
    """
    selected   = 'objects.objectId'
    tables     = 'objects'
    conditions = ''
    e = check_query(selected, tables, conditions)
    if e:
        print('ERROR in create_lightweight_query!', e)
        return
    real_sql = build_query(selected, tables, conditions)

    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'REPLACE INTO myqueries ('
    query += 'mq_id, name, description, '
    query += 'selected, conditions, tables, '
    query += 'public, active, topic_name, real_sql, user)'
    query += ' VALUES ('
    query += '1, "Lightweight", "Heartbeat query for public Kafka", '
    query += '"objects.objectId", "", "objects",'
    query += '0, 2, "lasair_1Lightweight", "%s", %d'
    query += ')'
    query = query % (real_sql, user_id)
    cursor.execute(query)
    msl.commit()

def create_sample_email_query(user_id):
    """ An email query to make sure system works
    Sends email to the address associated with the given user.
    Just a few alerts will be brighter than mag 14!
    """
    selected   = 'objects.objectId'
    tables     = 'objects'
    conditions = 'gmag < 14'
    e = check_query(selected, tables, conditions)
    if e:
        print('ERROR in create_lightweight_query!', e)
        return
    real_sql = build_query(selected, tables, conditions)

    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'REPLACE INTO myqueries ('
    query += 'mq_id, name, description, '
    query += 'selected, conditions, tables, '
    query += 'public, active, topic_name, real_sql, user)'
    query += ' VALUES ('
    query += '2, "Sample Email", "Sample to check email queries", '
    query += '"%s", "%s", "%s",'
    query += '0, 1, "lasair_1SampleEmail", "%s", %d'
    query += ')'
    query = query % (selected, conditions, tables, real_sql, user_id)
#    print(query)
    cursor.execute(query)
    msl.commit()

def create_fast_sample_annotator(username, user_id):
    """ Test the fast annotation system.
    Annotator has active=2, so annotations received are processed 
    next time the filter nodes run.
    """
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'REPLACE INTO annotators ('
    query += 'topic, description, username, '
    query += 'active, public, user)'
    query += ' VALUES ('
    query += '"sample_fast", "Sample fast annotator", "%s", '
    query += '2, 0, %d'
    query += ')'
    query = query % (username, user_id)
    print(query)
    cursor.execute(query)
    msl.commit()

def create_fast_annotation_query(user_id):
    """ Example of a query that uses the fast annotation system.
    When an update comes from the sample annotator (function above)
    an alert is pushed to public kafka as soon as the filter nodes run
    """
    selected = 'objects.objectId, sample_fast.classification, sample_fast.explanation, sample_fast.classdict'
    tables = 'objects, annotator:sample_fast'
    conditions = ''
    e = check_query(selected, tables, conditions)
    if e:
        print('ERROR in create_fast_annotation_query!', e)
        return
    real_sql = build_query(selected, tables, conditions)
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'REPLACE INTO myqueries ('
    query += 'mq_id, name, description, '
    query += 'selected, conditions, tables, '
    query += 'public, active, topic_name, real_sql, user)'
    query += ' VALUES ('
    query += '3, "Sample Fast", "Sample fast annotator query", '
    query += '"%s", "%s", "%s", '
    query += '0, 2, "lasair_1Sample_Fast", '
    query += "'%s', %d"
    query += ')'
    query = query % (selected, conditions, tables, real_sql, user_id)
    print(query)
    cursor.execute(query)
    msl.commit()


if __name__ == "__main__":
    username = 'su'

    user_id = get_id_for_username(username)
    print('username %s has id %d' % (username, user_id))

    radius = 5 # arcseconds
    try:
        create_TNS(user_id, radius)
        print('TNS created')
    except:
        print('TNS not created ... already exists?')

    create_lightweight_query(user_id)
    print('Lightweight query created')

    create_sample_email_query(user_id)
    print('Sample Email query created')

    create_fast_sample_annotator(username, user_id)
    print('Fast annotator created')

    create_fast_annotation_query(user_id)
    print('Fast annotator query created')
