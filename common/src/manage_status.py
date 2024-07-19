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
import db_connect

class manage_status():
    """ manage_status.
    """
    def __init__(self):
        self.msl = db_connect.remote()

    def read(self, nid):
        cursor  = self.msl.cursor(buffered=True, dictionary=True)
        query = 'SELECT name,value FROM lasair_statistics WHERE nid=%d' % nid
        cursor.execute(query)
        dict = {}
        for row in cursor:
            dict[row['name']] = row['value']
        return dict

    def delete(self, nid=False):
        cursor  = self.msl.cursor(buffered=True, dictionary=True)
        query = 'DELETE FROM lasair_statistics '
        if nid:
            query += ' WHERE nid=%d' % nid
        cursor.execute(query)
        self.msl.commit()

    def tostr(self, nid):
        return json.dumps(self.read(nid), indent=2)

    def set(self, dictionary, nid):
        query = "REPLACE INTO lasair_statistics (nid,name,value) VALUES "
        ql = []
        for name,value in dictionary.items():
            ql.append("(%d,'%s',%f)" % (nid, name, value))
        query += ','.join(ql)
#        print(query)
        cursor  = self.msl.cursor(buffered=True, dictionary=True)
        cursor.execute(query)
        self.msl.commit()

    def add(self, dictionary, nid):
        queryfmt = "INSERT INTO lasair_statistics (nid,name,value) VALUES "
        queryfmt += "(%d,'%s',%f) ON DUPLICATE KEY UPDATE value=value+%f"
        cursor  = self.msl.cursor(buffered=True, dictionary=True)
        for name,value in dictionary.items():
            query = queryfmt % (nid, name, value, value)
#            print(query)
            cursor.execute(query)
        self.msl.commit()

# A timing class built with manage_status
class timer():
    def __init__(self, nameroot):
        try:
            # assume a hostname like lasair-lsst-dev-ingest-0 and append the 0
            hostnum = socket.gethostname().split('-')[-1]
        except:
            hostnum = '0'
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

if __name__ == "__main__":
    def assertEqual(a,b):
        assert(a==b)

    ms = manage_status()
    ms.delete(6)
    ms.set({'banana':5, 'orange':6}, 6)
    ms.add({'apple':12, 'pear':7},   6)
    ms.add({'apple':12, 'pear':1},   6)
    status = ms.read(6)
    print(status)
    ms.delete(6)

    assertEqual(status['banana'], 5)
    assertEqual(status['orange'], 6)
    assertEqual(status['apple'], 24)
    assertEqual(status['pear'],   8)
