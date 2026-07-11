import sys
sys.path.append('../../../common')
import settings
sys.path.append('../../../common/src')
import db_connect, annotator

USERNAME = 'royg'
msl = None

def make_annotator():
    cursor =  msl.cursor(buffered=True, dictionary=True)

    # find user id number for given username
    query = f'SELECT id FROM auth_user WHERE username="{USERNAME}"'
    cursor.execute(query)
    for row in cursor:
        id = row['id']
    print(f'{USERNAME} is user number {id}')

    # make the tags_ annotator
    query = 'INSERT INTO annotators (topic, active, public, user) '
    query += f'VALUES ("tags_{USERNAME}", 1, 0, {id})'
    print(query)
    cursor.execute(query)

def make_annotation():
    cursor =  msl.cursor(buffered=True, dictionary=True)

    # find an object
    query = f'SELECT diaObjectId FROM objects LIMIT 1'
    cursor.execute(query)
    for row in cursor:
        diaObjectId = row['diaObjectId']
    print(f'diaObjectId is {diaObjectId}')

    topic = f'tags_{USERNAME}'
    annotator.insert_annotation(diaObjectId, topic, 'apple')
    annotator.insert_annotation(diaObjectId, topic, 'pear')



if __name__ == '__main__':
    if settings.WEB_DOMAIN != 'lasair-lsst-dev':
        print('This test can only run on the dev system')
        sys.exit()
    msl = db_connect.remote()
#    make_annotator()
    make_annotation()
    msl.commit()


