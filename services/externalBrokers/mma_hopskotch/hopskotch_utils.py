import os, sys
import signal
from hop import Stream
from hop.auth import Auth
from hop.io import StartPosition

def handler(signum, frame):
    raise TimeoutError

class hop_reader():
    def __init__(self, username, password, topic, my_group_id, earliest=False):
        hop_auth = Auth(username, password)

        # By default only listen to alerts that appear after the daemon has started.
        start_position = StartPosition.LATEST

        # Or go back to the earliest message in the queue.
        if earliest:
            start_position = StartPosition.EARLIEST

        stream = Stream(
            auth=hop_auth,
            start_at=start_position,
            until_eos=False
        )

        url = f"kafka://kafka.scimma.org/{topic}"
        group_id = f"{username}-{my_group_id}"

        self.hop_stream = stream.open( url, "r", group_id=group_id).read()

    def poll(self):
        alert = next(self.hop_stream)
        return alert.content
