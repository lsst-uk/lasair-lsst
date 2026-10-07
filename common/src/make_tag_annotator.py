""" Create a tags annotator for every (or just one) user
If an argument is supplied, it is assumed to be a username.
For each username, an annotator is made with the topic "tags_username"
"""
import sys
sys.path.append('../common/src')
import db_connect


def make_annotator(msl, username, id, verbose=False):
    """Create the tags_<username> annotator for a user, if it does not exist.

    Idempotent: `annotators.topic` is the primary key and the insert is
    `INSERT IGNORE`, so calling this for a user who already has an annotator
    is a no-op. Database errors are raised, never swallowed, because callers
    report success on the strength of this function returning.

    Args:
        msl: an open connection to the main database
        username: the user's name, used to build the topic
        id: the user's `auth_user.id`
        verbose: print the SQL query on stdout

    Raises:
        mysql.connector.errors.Error: database error
    """
    cursor = msl.cursor(buffered=True, dictionary=True)
    # MAKE THE tags_ ANNOTATOR
    query = 'INSERT IGNORE INTO annotators (topic, active, public, user) '
    query += 'VALUES (%s, 1, 0, %s)'
    params = ('tags_%s' % username, id)
    if verbose: print(query, params)
    cursor.execute(query, params)


if __name__ == "__main__":
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    verbose = False

    query = 'SELECT username, id FROM auth_user'
    params = ()
    if len(sys.argv) > 1:
        query += ' WHERE username=%s'
        params = (sys.argv[1],)
    if verbose: print(query, params)
    cursor.execute(query, params)
    for row in cursor:
        make_annotator(msl, row['username'], row['id'], verbose)
        print(f'tags annotator made for {row["username"]}')
    msl.commit()
