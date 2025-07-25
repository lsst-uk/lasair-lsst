"""
manage_status.py
Manage a set of status files that is a set of name-value pairs in JSON.
Different processes/cores/threads can change name/value or increment values.
There are different dictionaries for different values of the integer 'nid"
The values can only be floats.
CREATE TABLE lasair_statistics (
    nid int NOT NULL,
    name VARCHAR(32),
    value FLOAT DEFAULT 0,
    PRIMARY key (nid,name)
);
"""

import sys
import json
import time
import socket
try:
    sys.path.append('../../../common/')
    import src.db_connect as db_connect
except:
    pass

class manage_status():
    """ manage_status.
    """
    def __init__(self, msl=None, table='lasair_statistics', log=None):
        if msl:
            self.msl = msl
        else:
            self.msl = db_connect.remote()
        self.table = table
        self.log = log

    def read(self, nid):
        cursor  = self.msl.cursor(buffered=True, dictionary=True)
        query = 'SELECT name,value FROM %s WHERE nid=%d' % (self.table, nid)
        cursor.execute(query)
        dict = {}
        for row in cursor:
            dict[row['name']] = row['value']
        return dict

    def delete(self, nid=False):
        cursor  = self.msl.cursor(buffered=True, dictionary=True)
        query = 'DELETE FROM %s ' % self.table
        if nid:
            query += ' WHERE nid=%d' % nid
        cursor.execute(query)
        self.msl.commit()

    def tostr(self, nid):
        return json.dumps(self.read(nid), indent=2)

    def execute_with_retry(self, query, max_retries=5, initial_wait=1):
        wait_time = initial_wait
        cursor  = self.msl.cursor(buffered=True, dictionary=True)
        for attempt in range(1, max_retries + 1):
            try:
                cursor.execute(query)
                self.msl.commit()
                return  # Success, exit the function
            except Exception as e:
                if attempt < max_retries:
                    if self.log: 
                        self.log.warning("manage_status: Retrying in %.1f seconds...%s" % (wait_time, str(e)))
                    time.sleep(wait_time)
                    wait_time *= 2  # Double the wait time
                else:
                    if self.log: 
                        self.log.warning("manage_status: All retries failed. Giving up.")
                    return

    def set(self, dictionary, nid):
        query = "REPLACE INTO %s (nid,name,value) VALUES " % self.table
        ql = []
        for name,value in dictionary.items():
            ql.append("(%d,'%s',%f)" % (nid, name, value))
        query += ','.join(ql)
#        print(query)
        self.execute_with_retry(query)

    def add(self, dictionary, nid):
        queryfmt = "INSERT INTO %s (nid,name,value) VALUES " % self.table
        queryfmt += "(%d,'%s',%f) ON DUPLICATE KEY UPDATE value=value+%f"
        cursor  = self.msl.cursor(buffered=True, dictionary=True)
        for name,value in dictionary.items():
            query = queryfmt % (nid, name, value, value)
#            print(query)
            self.execute_with_retry(query)

# A timing class built with manage_status
class timer():
    def __init__(self, nameroot):
        try:
            # assume a hostname like lasair-lsst-dev-ingest-0 and append the 0
            hostnum = socket.gethostname().split('-')[-1]
        except:
            hostnum = 'Z'
        self.name = nameroot + '_' + hostnum
        self.start = time.perf_counter()
        self.elapsed = 0.0

    def on(self):
        # start the clock
        self.start = time.perf_counter()

    def off(self):
        # stop the clock
        delta = time.perf_counter() - self.start
        self.elapsed += delta

    def add2ms(self, ms, nid):
        ms.add({self.name:self.elapsed}, nid)
        self.elapsed = 0.0
