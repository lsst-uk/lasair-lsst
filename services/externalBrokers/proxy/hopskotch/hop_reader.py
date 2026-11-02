import os, sys
from hop import Stream
from hop.auth import Auth
from hop.io import StartPosition
from proxy_annotators import ProxyAnnotator
import signal


def handler(signum, frame):
    raise TimeoutError


signal.signal(signal.SIGALRM, handler)


class HopReader(ProxyAnnotator):
    def __init__(self, settings):
        super().__init__(settings)
        username = settings['SCIMMA_AUTH_USERNAME']
        password = settings['SCIMMA_AUTH_PASSWORD']
        hop_auth = Auth(username, password)
        stream = Stream(auth=hop_auth, start_at=StartPosition.EARLIEST)
        url = 'kafka://kafka.scimma.org/' + settings['MODULE']
        if 'group_id' in settings:
            my_group_id = settings['group_id']
        else:
            my_group_id = 'test123'
        group_id = username + '-' + my_group_id
        self.hop_stream = stream.open(url, "r", group_id=group_id).read()
        self.timeout = settings.get('TIMEOUT', 5)
        self.retries = settings.get('RETRIES', 4)

    def poll(self):
        try:
            alert = next(self.hop_stream)
        except StopIteration:
            return {'error': 'No more messages'}
        return alert.content

    def parse(self, result: dict) -> dict:
        """Parse the returned message."""
        raise NotImplementedError("Method must be implemented in subclass")

    def next_ann(self):
        for _ in range(self.retries):
            signal.alarm(self.timeout)
            try:
                result = self.poll()
                return self.parse(result)
            except TimeoutError:
                pass
            finally:
                signal.alarm(0)
        return None