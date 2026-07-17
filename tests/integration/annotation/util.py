import sys
import time
sys.path.append('../../../common')
import settings
sys.path.append('../../../common/src')
import db_connect, annotate, topic_name
sys.path.append('../../../webserver/lasair')
from query_builder import build_query

msl        = db_connect.remote()
verbose    = False
sleep_time = 10

def delete_annotator(ann_topic):
    print(f'\nDeleting annotator {ann_topic}')
    cursor =  msl.cursor(buffered=True, dictionary=True)
    query = f'DELETE from annotators WHERE topic="{ann_topic}"'
    if verbose: print(query)
    cursor.execute(query)
    query = f'DELETE from annotations WHERE topic="{ann_topic}"'
    if verbose: print(query)
    cursor.execute(query)

def delete_filter(filter_name):
    print(f'\nDeleting filter {filter_name}')
    query = f'DELETE FROM myqueries where name="{filter_name}"'
    if verbose: print(query)
    cursor =  msl.cursor(buffered=True, dictionary=True)
    cursor.execute(query)

def get_userid(username):
    # find user id number for given username
    print(f'\nGet userid for username {username}')
    cursor =  msl.cursor(buffered=True, dictionary=True)
    query = f'SELECT id FROM auth_user WHERE username="{username}"'
    if verbose: print(query)
    cursor.execute(query)
    for row in cursor:
        id = row['id']
    if verbose: print(f'{username} is user number {id}')
    return id

def make_annotator(topic, username):
    id = get_userid(username)
    print(f'\nMaking annotator for topic {topic} owned by {username}')
    cursor =  msl.cursor(buffered=True, dictionary=True)
    # make the tags_ annotator
    query = 'INSERT INTO annotators (topic, active, public, user) '
    query += f'VALUES ("tags_{username}", 1, 0, {id})'
    if verbose: print(query)
    cursor.execute(query)

def get_diaObjectId():
    print('\nFinding an arbitrary diaObjectId')
    cursor =  msl.cursor(buffered=True, dictionary=True)
    # find an object
    query = f'SELECT diaObjectId FROM objects LIMIT 1'
    if verbose: print(query)
    cursor.execute(query)
    for row in cursor:
        diaObjectId = row['diaObjectId']
    print(f'diaObjectId is {diaObjectId}')
    return diaObjectId

def make_annotations_db(diaObjectId, topic):
    print('\nmaking annotations')
    cursor =  msl.cursor(buffered=True, dictionary=True)
    annotate.insert_annotation_db   (diaObjectId, topic, 'apple', verbose)
    annotate.insert_annotation_db   (diaObjectId, topic, 'pear', verbose)

def make_annotations_kafka(diaObjectId, topic):
    print('\nmaking annotations')
    cursor =  msl.cursor(buffered=True, dictionary=True)
    annotate.insert_annotation_kafka(diaObjectId, topic, 'banana')
    annotate.insert_annotation_kafka(diaObjectId, topic, 'orange')

def check_annotations(diaObjectId):
    print('\nchecking annotations')
    tags = annotate.tags_for_object(username, diaObjectId, verbose)
    print(f'Found tags for {diaObjectId}/{username}:', tags)

    tag = 'apple'
    objs = annotate.objects_for_tag(username, tag, verbose)
    print(f'Found objects for {username}/{tag}:', objs)

def make_filter_ann(filter_name, username, ann_topic):
    id = get_userid(username)
    tn = topic_name.topic_name(id, filter_name)
    selected   = 'objects.diaObjectId'
    tables     = f'objects,annotator:{ann_topic}'
    conditions = ''
    sql = build_query(selected, tables, conditions)
    query = 'INSERT INTO myqueries '
    query += '(user, name, selected, conditions, tables, public, '
    query += 'run, output, byte_quota, topic_name, real_sql) '
    query += f'VALUES ({id}, "{filter_name}", "{selected}", "{conditions}", "{tables}", 0, '
    query += f'2, 2, 10000000, "{tn}", \'{sql}\')'
    print(f'\nMaking filter {filter_name}, topic name {tn}, uses annotation {ann_topic}')
    if verbose: print(query)
    cursor =  msl.cursor(buffered=True, dictionary=True)
    cursor.execute(query)


if __name__ == '__main__':
    if settings.WEB_DOMAIN != 'lasair-lsst-dev':
        print('This test can only run on the dev system')
        sys.exit()
    username = 'royg'
    ann_topic = f'tags_{username}'
    filter_name = f'__f{ann_topic}'
    delete_annotator(ann_topic)
    delete_filter(filter_name)
    msl.commit()

    make_filter_ann(filter_name, username, ann_topic)
    make_annotator(ann_topic, username)
    msl.commit()

    diaObjectId = get_diaObjectId()

    make_annotations_db(diaObjectId, ann_topic)
    check_annotations(diaObjectId)

    make_annotations_kafka(diaObjectId, ann_topic)
    time.sleep(sleep_time)  # wait for kafka
    check_annotations(diaObjectId)

    msl.commit()
