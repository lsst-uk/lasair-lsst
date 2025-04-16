"""Check Object Database Functions

Validate the functions used in the object database - currently only mjdnow.
"""

import mysql.connector
import argparse
import time

def get_mysql_mjdnow(conf):
    config = {
      'user': conf['user'], 
      'password': conf['password'], 
      'host': conf['host'], 
      'port': conf['port'], 
      'database': conf['database'], 
      }
    msl = mysql.connector.connect(**config)

    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'select mjdnow()'
    cursor.execute(query)
    mysql_names = []
    row = cursor.fetchone()
    return row['mjdnow()']

def get_mjdnow():
    mjdnow = time.time()/86400.0 + 40587
    return mjdnow

if __name__ == "__main__":
    # parse cmd line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user', default='ztf', type=str, help='MySQL username')
    parser.add_argument('--password', type=str, help='MySQL password')
    parser.add_argument('--host', type=str, help='MySQL hostname')
    parser.add_argument('--port', type=int, default=3306, help='MySQL port number')
    parser.add_argument('--database', type=str, default='ztf', help='Name of database')
    conf = vars(parser.parse_args())

    # difference between our calculation and db should be < 2s
    mysql_mjdnow = get_mysql_mjdnow(conf)
    mjdnow = get_mjdnow()
    difference = abs((mysql_mjdnow - mjdnow) * 86400.0)
    assert difference < 2, "Validation failed: difference = {}".format(difference)

    print('mysql functions OK')

