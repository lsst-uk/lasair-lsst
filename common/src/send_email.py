import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib


def send_email(to_addr: str, fname: str, message: str, message_html: str = None, message_json: str = None):
    msg = MIMEMultipart('mixed')
    body = MIMEMultipart('alternative')

    msg['Subject'] = f"Lasair query {fname}"
    msg['From'] = settings.LASAIR_EMAIL
    msg['To'] = to_addr

    body.attach(MIMEText(message, 'plain'))
    if message_html:
        body.attach(MIMEText(message_html, 'html'))
    msg.attach(body)
    if message_json:
        attachment = MIMEApplication(message_json, 'json', Name=f"{fname}.json")
        attachment.add_header('Content-Disposition', 'attachment', filename=f"{fname}.json")
        msg.attach(attachment)
    s = smtplib.SMTP('localhost')
    s.sendmail('lasair@lsst.ac.uk', to_addr, msg.as_string())