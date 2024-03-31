import smtplib
from email.mime.text import MIMEText

from fbsurvivor.settings import ENV, SMTP_PASSWORD, SMTP_SENDER, SMTP_SERVER, SMTP_USER


def send_email(subject, recipients, message):
    if ENV == "dev":
        print(f"\n\nSending Email to {len(recipients)} players...\n{subject}\n\n{message}\n\n")
        return

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = SMTP_SENDER
    msg["To"] = SMTP_SENDER

    conn = smtplib.SMTP_SSL(SMTP_SERVER)
    conn.login(SMTP_USER, SMTP_PASSWORD)
    try:
        conn.sendmail(SMTP_SENDER, recipients, msg.as_string())
    finally:
        conn.quit()
