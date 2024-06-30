"""
manage_status.py
Manage a set of status files that is a set of key-value pairs in JSON. 
Different processes/cores/threads can change key value or increment values.
There is a "file_id" to determine which file we are working with
"""

import datetime
import json
import time
import socket
import os, sys
import fcntl
SLEEPTIME = 0.1

class manage_status():
    """ manage_status.
        Args:
            file_id: The special key, when its value changes, increment from zero
            status_file: Name of the status file
    """
    def __init__(self, status_file_root):
        self.status_file_root  = status_file_root

    def read(self, file_id):
        status_file = '%s_%s.json' % (self.status_file_root, str(file_id))
        f = open(status_file)
        s = f.read()
        status = json.loads(s)
        f.close()
        return status

    def lock_read(self, file_id):
        """ lock_read.
            If status file not present, make an empty one
            Waits for lock, then locks and returns the status
            Must be quickly followed with write_unlock!
            Args:
                file_id: which file to use
        """
        status_file = '%s_%s.json' % (self.status_file_root, str(file_id))
        lock_file   = '%s.lock' % self.status_file_root
    
        if not os.path.exists(status_file) and not os.path.exists(lock_file):
#            print('Status file not present!')
            f = open(status_file, 'w')
            f.write('{}')
            f.close()

        # wait until the lock is released
        # but if we wait 100 times, just kill the lock and go ahead
        for n in range(100):
            if not os.path.exists(lock_file):
                break
            time.sleep(SLEEPTIME)
        else:
            os.remove(lock_file)
    
        # lock the directory for me
        lock = open(lock_file, 'w')
        lock.close()

        # return contents
        f = open(status_file)
        try:
            status = json.loads(f.read())
            f.close()
        except:
            status = {}
        return status
    
    def write_unlock(self, status, file_id):
        """ write_status:
            Writes the status file, then unlocks
            Args:
                status: dictionary of key-value pairs
                file_id: which file to use
        """
        update_time = datetime.datetime.utcnow().isoformat()
        update_time = update_time.split('.')[0]
        status['update_time'] = update_time
    
        status_file = '%s_%s.json' % (self.status_file_root, str(file_id))
        lock_file   = '%s.lock' % self.status_file_root
    
        # dump the status
        os.remove(status_file)
        f = open(status_file, 'w')
        s = {key:status[key] for key in sorted(status.keys())}
        f.write(json.dumps(s))
        f.close()

        # remove the lock file
        os.remove(lock_file)
    
    def tostr(self, file_id):
        """ __repr__:
            Write out the status file
        """
        status_file = '%s_%s.json' % (self.status_file_root, str(file_id))
        try:
            f = open(status_file)
            status = json.loads(f.read())
            f.close()
        except:
            status = {}
        return json.dumps(status, indent=2)

    def set(self, dictionary, file_id):
        """ set.
            Puts the kv pairs from the dictionary into the status file
            Args:
                dictionary: set of key-value pairs
                file_id: which file to use
        """
        status = self.lock_read(file_id)
        for key,value in dictionary.items():
            status[key] = value
        self.write_unlock(status, file_id)

    def add(self, dictionary, file_id):
        """ add
            Increments the given keys with the given values
            Args:
                dictionary: set of key-value pairs
                file_id: if same as in status file, increment, else set
        """
        status = self.lock_read(file_id)

        for key,value in dictionary.items():
            if key in status: status[key] += value
            else:             status[key]  = value

        self.write_unlock(status, file_id)

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

    os.system('mkdir play')
    ms = manage_status('play/status')
    ms.set({'banana':5, 'orange':6}, 6)
    ms.add({'apple':12, 'pear':7},   6)
    ms.add({'apple':12, 'pear':1},   6)

    ms.add({'apple':1, 'pear':7},    7)
    ms.add({'apple':1, 'pear':7},    7)
    ms.set({'banana':5, 'orange':6}, 7)
    ms.set({'banana':4, 'orange':7}, 7)
    ms.set({'banana':3, 'orange':8}, 7)

    status = ms.read(6)
    print(status)
    assertEqual(status['banana'], 5)
    assertEqual(status['orange'], 6)
    assertEqual(status['apple'], 24)
    assertEqual(status['pear'],   8)

    status = ms.read(7)
    print(status)
    assertEqual(status['banana'], 3)
    assertEqual(status['orange'], 8)
    assertEqual(status['apple'],  2)
    assertEqual(status['pear'],  14)

    # delete the play area
    os.system('rm -r play')

