import sys
sys.path.append('../common')
from src import db_connect
sys.path.append('../webserver/lasair')
from query_builder import check_query, build_query

def check_query_syntax(mq_id, update=False):
    msl = db_connect.remote()
    message = 'checking query %d' % mq_id
    query = 'SELECT selected, conditions, tables FROM myqueries WHERE mq_id=%d'
    query = query % mq_id
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute(query)
    for row in cursor:
        s = row['selected']
        f = row['tables']
        w = row['conditions']
        break

    e = check_query(s, f, w)
    if e:
        print(e)
    else:
        real_sql = build_query(s, f, w)
#        print(real_sql)
    try:
        cursor.execute(real_sql + ' LIMIT 0')
        message += ' --> OK'
        good = True
    except Exception as e:
        message += ' ' + str(e)
        good = False

    if update and good:
        query = "UPDATE myqueries SET real_sql='%s' WHERE mq_id=%d" % (real_sql, mq_id)
        print(query)
        cursor.execute(query)
        msl.commit()
        message += ' real_sql updated'
    return message

if __name__ == "__main__":
    if len(sys.argv) > 1:
        mq_id = int(sys.argv[1])
        message = check_query_syntax(mq_id, True)
        print(message)
    else:
        query = 'SELECT mq_id FROM myqueries ORDER BY mq_id'
        msl = db_connect.remote()
        cursor = msl.cursor(buffered=True, dictionary=True)
        cursor.execute(query)
        for row in cursor:
            message = check_query_syntax(row['mq_id'], False)
            print(message)

