import sys
import time
sys.path.append('../../../common')
import settings
sys.path.append('../../../common/src')
import db_connect, annotator

username = 'royg'
msl = db_connect.remote()

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
    cursor.execute(query)

def make_annotations():
    print('\nmaking annotations')
    cursor =  msl.cursor(buffered=True, dictionary=True)

    # find an object
    query = f'SELECT diaObjectId FROM objects LIMIT 1'
    cursor.execute(query)
    for row in cursor:
        diaObjectId = row['diaObjectId']
    print(f'diaObjectId is {diaObjectId}')

    topic = f'tags_{username}'
    annotator.insert_annotation(diaObjectId, topic, 'apple')
    annotator.insert_annotation(diaObjectId, topic, 'pear')

def check_annotations():
    print('\nchecking annotations')
    tags = annotator.tags_for_object(username, diaObjectId)
    print(f'Found tags for {diaObjectId}/{username}:', tags)

    tag = 'apple'
    objs = annotator.objects_for_tag(username, tag)
    print(f'Found objects for {username}/{tag}:', objs)

if __name__ == '__main__':
    if settings.WEB_DOMAIN != 'lasair-lsst-dev':
        print('This test can only run on the dev system')
        sys.exit()
    clean()
    make_annotator()
    make_annotations()
    time.sleep(300)
    check_annotations()
    msl.commit()
