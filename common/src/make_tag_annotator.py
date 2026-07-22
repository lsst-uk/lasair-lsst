""" Create a tags annotator for every (or just one) user
If an argument is supplied, it is assumed to be a username.
For each username, an annotator is made with the topic "tags_username"
"""
import sys
import db_connect

def make_annotator(msl, username, id, verbose=False):
    cursor =  msl.cursor(buffered=True, dictionary=True)
    # make the tags_ annotator
    query = 'INSERT INTO annotators (topic, active, public, user) '
    query += f'VALUES ("tags_{username}", 1, 0, {id})'
    if verbose: print(query)
    try:
        cursor.execute(query)
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    msl = db_connect.remote()
    cursor =  msl.cursor(buffered=True, dictionary=True)
    verbose = False

    query = f'SELECT username, id FROM auth_user '
    if len(sys.argv) > 1:
        username = sys.argv[1]
        query += f'WHERE username="{username}"'
    if verbose: print(query)
    cursor.execute(query)
    for row in cursor:
        make_annotator(msl, row['username'], row['id'], verbose)
        print(f'tags annotator made for {row['username']}')
    msl.commit()

