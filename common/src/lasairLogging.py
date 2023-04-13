"""Common Lasair logging module. Based on standard logging module with sensible default
values for Lasair. Sets up a log file and also sends error and above messages to Slack."""

import os, logging
from slack_webhook import SlackWebhook


class SlackHandler(logging.Handler):
    """Logging handler to send Slack messages."""
    def __init__(self, webhook: SlackWebhook):
        super().__init__()
        self.webhook = webhook

    def emit(self, record):
        """Emit a record."""
        msg = self.format(record)
        self.webhook.send(msg)


class DuplicateFilter(logging.Filter):
    """Filter to suppress multiple identical Slack messages."""
    def __init__(self, webhook: SlackWebhook, maxmerge):
        super().__init__()
        self.n_msg = 0
        self.webhook = webhook
        self.maxmerge = maxmerge

    def filter(self, record):
        current_log = (record.levelno, record.msg)
        if current_log != getattr(self, "last_log", None) or self.n_msg >= self.maxmerge:
            if self.n_msg > 0:
                self.webhook.send("Suppressed {} identical messages".format(self.n_msg))
            self.last_log = current_log
            self.n_msg = 0
            return True
        self.n_msg += 1
        return False


def basicConfig(filename: str = None,
                stream=None,
                webhook: SlackWebhook = None,
                level=logging.INFO,
                force=False,
                merge=False,
                maxmerge=20):
    fmt = "[%(asctime)s] %(levelname)s: %(funcName)s: %(message)s"
    if filename is None and stream is None:
        # Don't log anything - presumably Slack only
        logging.basicConfig(filename="/dev/null", level=level, format=fmt, force=force)
    elif stream is None:
        # Log to file only
        logging.basicConfig(filename=filename, level=level, format=fmt, force=force)
    elif filename is None:
        # Log to stream only
        logging.basicConfig(stream=stream, level=level, format=fmt, force=force)
    else:
        # Log to both file and stream
        logging.basicConfig(filename=filename, level=level, format=fmt, force=force)
        stream_formatter = logging.Formatter(fmt)
        stream_handler = logging.StreamHandler(stream)
        stream_handler.setLevel(level)
        stream_handler.setFormatter(stream_formatter)
        logging.getLogger().addHandler(stream_handler)
    if webhook is not None:
        # Set up Slack alerting
        hostname = os.uname().nodename
        slack_formatter = logging.Formatter(
            "%(levelname)s: {}: %(funcName)s: %(message)s".format(hostname))
        slack_handler = SlackHandler(webhook)
        slack_handler.setLevel(logging.ERROR)
        slack_handler.setFormatter(slack_formatter)
        logging.getLogger().addHandler(slack_handler)
        if merge:
            slack_handler.addFilter(DuplicateFilter(webhook, maxmerge))


def getLogger(name):
    return logging.getLogger(name)


def shutdown():
    logging.shutdown()
