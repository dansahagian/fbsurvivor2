import datetime
import secrets
import smtplib
from email.mime.text import MIMEText

import pytz

from fbsurvivor import settings


def get_localized_right_now():
    return pytz.timezone("US/Pacific").localize(datetime.datetime.now())


def generate_code() -> int:
    return secrets.choice(range(111111, 1000000))


def send_email(subject, recipients, message):
    sender = settings.SMTP_SENDER

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = sender

    conn = smtplib.SMTP_SSL(settings.SMTP_SERVER)
    conn.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    try:
        conn.sendmail(sender, recipients, msg.as_string())
    finally:
        conn.quit()