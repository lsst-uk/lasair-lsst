"""
Query checker for Lasair.
    for all or one query, run it with LIMIT=0 or not
    and timeout=0 or not

Usage:
    check_query_syntax.py [--mq_id=mq_id] [--limit=limit] [--timeout=timeout]
                          [--verbose] [--update]

Options:
    --mq_id=mq_id         Run only for a specific query
    --limit=limit         Run each query with SQL LIMIT [default: 0]
    --timeout=timeout     Run each query with a timeout in seconds, [default: 10]
    --update              Update the real_sql attribute of the query, [default: False]
    --verbose             Verbose mode, [default: False]
"""
from docopt import docopt
import sys
sys.path.append('../common')
from src import db_connect
sys.path.append('../webserver/lasair')
from query_builder import check_query, build_query_for_filter

def check_query_syntax(mq_id, limit='0', timeout='0', update=False, verbose=False):
    msl = db_connect.remote()
    message = 'checking query %d' % mq_id
    # THE OWNER'S USERNAME COMES ALONG, SO real_sql CARRIES THEIR HIDDEN EXCLUSION
    query = 'SELECT selected, conditions, tables, auth_user.username AS username '
    query += 'FROM myqueries JOIN auth_user ON auth_user.id = myqueries.user '
    query += 'WHERE mq_id=%s'
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute(query, (mq_id,))
    for row in cursor:
        s = row['selected']
        f = row['tables']
        w = row['conditions']
        break

    e = check_query(s, f, w)
    if e:
        print(e)
    else:
        try:
            real_sql = build_query_for_filter(row, is_owner=True)
        except Exception as e:
            message = 'Query building failed %s\n%s\n%s\n%s\n' % (str(e), s, f, w)
            return message
#        print(real_sql)
    timeout = int(timeout)
    if timeout > 0:
        realreal_sql = ('SET STATEMENT max_statement_time=%d FOR %s LIMIT %s' \
            % (timeout, real_sql, limit))
    else:
        realreal_sql = ('%s LIMIT %s' % (real_sql, limit))

    if verbose:
        print('Query %s is:\n%s\n' % (mq_id, realreal_sql))
    try:
        cursor.execute(realreal_sql)
        message += ' --> OK'
        good = True
    except Exception as e:
        message += ' ' + str(e)
        good = False

    if update and good:
        query = 'UPDATE myqueries SET real_sql=%s WHERE mq_id=%s'
        print(query, (real_sql, mq_id))
        cursor.execute(query, (real_sql, mq_id))
        msl.commit()
        message += ' real_sql updated'
    return message

if __name__ == "__main__":
    args = docopt(__doc__)

    # if there is a specific query, check it and update it
    if args['--mq_id']: 
        mq_id = int(args['--mq_id'])
        message = check_query_syntax(mq_id, 
            limit =args['--limit'],  timeout=args['--timeout'], 
            update=args['--update'], verbose=args['--verbose'])
        print(message)

    # if no specific query, just check them all
    else:
        query = 'SELECT mq_id FROM myqueries ORDER BY mq_id'
        msl = db_connect.remote()
        cursor = msl.cursor(buffered=True, dictionary=True)
        cursor.execute(query)
        for row in cursor:
            message = check_query_syntax(row['mq_id'],  
                limit =args['--limit'],  timeout=args['--timeout'], 
                update=args['--update'], verbose=args['--verbose'])
            print(message)
