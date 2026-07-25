import os, sys
import signal
from hop import Stream
from hop.auth import Auth
from hop.io import StartPosition

def handler(signum, frame):
    raise TimeoutError

class hop_reader():
    def __init__(self, settings):
        username = settings['SCIMMA_AUTH_USERNAME']
        password = settings['SCIMMA_AUTH_PASSWORD']
        hop_auth = Auth(username, password)
        stream   = Stream(auth=hop_auth, start_at=StartPosition.EARLIEST)
        url      = 'kafka://kafka.scimma.org/' + settings['MODULE']
        my_group_id = 'test123'
        group_id = username + '-' + my_group_id
        self.hop_stream = stream.open(url, "r", group_id=group_id).read()

    def poll(self):
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(10) 
        alert = next(self.hop_stream)
        signal.alarm(0)
        return alert.content

