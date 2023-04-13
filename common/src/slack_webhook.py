import sys, requests, json, os
import argparse
import warnings


class SlackWebhook():
    """Represents a Slack app or integration that we can send messages to."""

    def __init__(self, url: str, channel: str = None):
        self.url = url
        self.channel = channel

    def send(self, message: str):
        """Send a message."""
        _send(self.url, message, self.channel)


def send(url, message):
    """Send a message to the specified URL (deprecated)."""
    warnings.warn("Direct use of send is deprecated, please use LasairLogging.",
                  DeprecationWarning, stacklevel=2)
    _send(url, message, channel='#general')


def _send(url, message, channel):
    data = {'text': message}
    if channel is not None:
        data['channel'] = channel
    response = requests.post(url, data=json.dumps(data),
                             headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


if __name__ == "__main__":
    """Read from stdin and send each line as a message."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-u', '--url', required=True, type=str, help='Webhook URL')
    conf = vars(parser.parse_args())

    for line in sys.stdin:
        send(conf['url'], line.rstrip())

