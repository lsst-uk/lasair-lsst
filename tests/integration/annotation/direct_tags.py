import sys
import time
sys.path.append('../../../common')
import settings
sys.path.append('../../../common/src')
import db_connect, annotate

# some global variables
username    = 'royg'
msl         = db_connect.remote()

def clean():
    print('cleaning up')
    cursor =  msl.cursor(buffered=True, dictionary=True)
    topic = f'tags_{username}'
    query = f'DELETE from annotators WHERE topic="{topic}"'
    cursor.execute(query)
    query = f'DELETE from annotations WHERE topic="{topic}"'
    cursor.execute(query)

def make_annotator():
    print('\nmaking annotator')
    cursor =  msl.cursor(buffered=True, dictionary=True)

    # find user id number for given username
    query = f'SELECT id FROM auth_user WHERE username="{username}"'
    cursor.execute(query)
    for row in cursor:
        id = row['id']
    print(f'{username} is user number {id}')

    # make the tags_ annotator
    query = 'INSERT INTO annotators (topic, active, public, user) '
    query += f'VALUES ("tags_{username}", 1, 0, {id})'
    print(query)
    try:
        cursor.execute(query)
    except Exception as e:
        print(str(e))

def make_annotations():
    print('\nmaking annotations')
    cursor =  msl.cursor(buffered=True, dictionary=True)

    # find an object
    query = f'SELECT diaObjectId FROM objects LIMIT 1'
    cursor.execute(query)
    for row in cursor:
        diaObjectId = row['diaObjectId']
    print(f'diaObjectId is {diaObjectId}')

    # use the annotations modulw to insert
    topic = f'tags_{username}'
    annotate.insert_annotation_db   (diaObjectId, topic, 'apple')
    annotate.insert_annotation_db   (diaObjectId, topic, 'pear')
    annotate.insert_annotation_kafka(diaObjectId, topic, 'banana')
    annotate.insert_annotation_kafka(diaObjectId, topic, 'orange')
    return diaObjectId

def check_annotations(diaObjectId):
    print('\nchecking annotations')
    tags = annotate.tags_for_object(username, diaObjectId)
    print(f'Found tags for {diaObjectId}/{username}:', tags)

    tag = 'apple'
    objs = annotate.objects_for_tag(username, tag)
    print(f'Found objects for {username}/{tag}:', objs)

if __name__ == '__main__':
    if settings.WEB_DOMAIN != 'lasair-lsst-dev':
        print('This test can only run on the dev system')
        sys.exit()
    clean()
    make_annotator()
    diaObjectId = make_annotations()
    check_annotations(diaObjectId)
    time.sleep(300)  # wait for kafka
    check_annotations(diaObjectId)
    msl.commit()
