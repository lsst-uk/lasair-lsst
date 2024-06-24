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
        try:
            f = open(status_file)
            status = json.loads(f.read())
            f.close()
        except:
            status = {}
        return status

    def write(self, status, file_id):
        """ write_status:
            Writes the status file
            Args:
                status: dictionary of key-value pairs
                file_id: which file to use
        """
        update_time = datetime.datetime.utcnow().isoformat()
        update_time = update_time.split('.')[0]
        status['update_time'] = update_time

        status_file = '%s_%s.json' % (self.status_file_root, str(file_id))

        # dump the status
        f = open(status_file, 'w')
        f.write(json.dumps(status))
        f.close()

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
        status = self.read(file_id)
        for key,value in dictionary.items():
            status[key] = value
        self.write(status, file_id)

    def add(self, dictionary, file_id):
        """ add
            Increments the given keys with the given values
            Args:
                dictionary: set of key-value pairs
                file_id: if same as in status file, increment, else set
        """
        status = self.read(file_id)

        for key,value in dictionary.items():
            if key in status: status[key] += value
            else:             status[key]  = value

        self.write(status, file_id)

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
