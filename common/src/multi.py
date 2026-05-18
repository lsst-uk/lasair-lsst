import sys
sys.path.append('..')
import settings
import mysql.connector
        
def remote(allow_infile=False):
    config = {
        'user'    : settings.DB_USER_READWRITE,
        'password': settings.DB_PASS_READWRITE,
        'host'    : settings.DB_HOST,
        'port'    : settings.DB_PORT,
        'database': 'ztf'
    }
    if allow_infile:
        config['allow_local_infile'] = True
    return mysql.connector.connect(**config)

if __name__=='__main__':
    msl = remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'select mq_id from myqueries limit 5;select mq_id from myqueries limit 5'
    cursor.execute(query)
    result_set = cursor.fetchall()
    msl.commit()


