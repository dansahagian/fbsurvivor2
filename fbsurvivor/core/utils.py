import secrets
import smtplib
import string
from email.mime.text import MIMEText

from fbsurvivor import settings
from fbsurvivor.core.models import Player


def generate_link() -> str:
    char_set = string.ascii_lowercase + string.digits
    link = "".join(secrets.choice(char_set) for _ in range(44))

    links = Player.objects.values_list("link", flat=True)

    if link in links:
        return generate_link()

    return link


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
