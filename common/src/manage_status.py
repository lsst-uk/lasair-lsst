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
from random import random
from multiprocessing import Process

###############
# acquire and release from Jiri Hnidek
# https://gist.github.com/jirihnidek/430d45c54311661b47fb45a3a7846537
def acquire(lock_file):
    open_mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC
    fd = os.open(lock_file, open_mode)

    pid = os.getpid()
    lock_file_fd = None

    timeout = 5.0
    start_time = current_time = time.time()
    while current_time < start_time + timeout:
        try:
            # The LOCK_EX means that only one process can hold the lock
            # The LOCK_NB means that the fcntl.flock() is not blocking
            # and we are able to implement termination of while loop,
            # when timeout is reached.
            # More information here:
            # https://docs.python.org/3/library/fcntl.html#fcntl.flock
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, OSError):
            pass
        else:
            lock_file_fd = fd
            break
        print(f'  {pid} waiting for lock')
        time.sleep(1.0)
        current_time = time.time()
    if lock_file_fd is None:
        os.close(fd)
    return lock_file_fd


def release(lock_file_fd):
    # Do not remove the lockfile:
    #
    #   https://github.com/benediktschmitt/py-filelock/issues/31
    #   https://stackoverflow.com/questions/17708885/flock-removing-locked-file-without-race-condition
    fcntl.flock(lock_file_fd, fcntl.LOCK_UN)
    os.close(lock_file_fd)
    return None
###############

class manage_status():
    """ manage_status.
        Args:
            file_id: The special key, when its value changes, increment from zero
            status_file: Name of the status file
    """
    def __init__(self, status_file_root):
        self.status_file_root  = status_file_root

    def read(self, file_id):
        status_file = '%s/status_%s.json' % (self.status_file_root, str(file_id))
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
        status_file = '%s/status_%s.json' % (self.status_file_root, str(file_id))
        lock_file   = '%s/lock' % self.status_file_root
        lock_file_fd = acquire(lock_file)

        if not os.path.exists(status_file):
#            print('Status file not present!')
            f = open(status_file, 'w')
            f.write('{}')
            f.close()

        # return contents
        f = open(status_file)
        try:
            status = json.loads(f.read())
            f.close()
        except:
            status = {}
        return (status, lock_file_fd)
    
    def write_unlock(self, status, file_id, lock_file_fd):
        """ write_status:
            Writes the status file, then unlocks
            Args:
                status: dictionary of key-value pairs
                file_id: which file to use
        """
        update_time = datetime.datetime.utcnow().isoformat()
        update_time = update_time.split('.')[0]
        status['update_time'] = update_time
    
        status_file = '%s/status_%s.json' % (self.status_file_root, str(file_id))
        lock_file   = '%s/lock' % self.status_file_root
    
        # dump the status
        os.remove(status_file)
        f = open(status_file, 'w')
        s = {key:status[key] for key in sorted(status.keys())}
        f.write(json.dumps(s, indent=2))
        f.close()

        # remove the lock file
        release(lock_file_fd)
    
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
        (status, lock_file_fd) = self.lock_read(file_id)
        for key,value in dictionary.items():
            status[key] = value
        self.write_unlock(status, file_id, lock_file_fd)

    def add(self, dictionary, file_id):
        """ add
            Increments the given keys with the given values
            Args:
                dictionary: set of key-value pairs
                file_id: if same as in status file, increment, else set
        """
        (status, lock_file_fd) = self.lock_read(file_id)

        for key,value in dictionary.items():
            if key in status: status[key] += value
            else:             status[key]  = value

        self.write_unlock(status, file_id, lock_file_fd)

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
