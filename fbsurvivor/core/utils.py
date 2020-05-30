import datetime
import smtplib
from email.mime.text import MIMEText

import pytz

from fbsurvivor import settings


def get_localized_right_now():
    return pytz.timezone("US/Pacific").localize(datetime.datetime.now())


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


def get_pretty_time(seconds):
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, remainder = divmod(remainder, 60)

    days = f"{int(days)} days" if days else ""
    hours = f"{int(hours)} hours" if hours else ""
    minutes = f"{int(minutes)} minutes" if minutes else ""

    if days and hours and minutes:
        return f"{days}, {hours}, & {minutes}"
    elif days and (hours or minutes):
        return f"{days} & {hours}{minutes}"
    elif hours and minutes:
        return f"{hours} & {minutes}"
    else:
        return f"{hours}{minutes}"
