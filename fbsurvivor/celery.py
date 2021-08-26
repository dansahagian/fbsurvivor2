from celery import Celery

from fbsurvivor.settings import BROKER_URL

app = Celery("fbsurvivor", broker=BROKER_URL)


@app.task()
def send_reminders_task():
    import pytz
    import datetime

    from twilio.rest import Client

    from fbsurvivor import settings
    from fbsurvivor.core.models import PlayerStatus, Season, Week
    from fbsurvivor.core.helpers import get_pretty_time

    current_season: Season = Season.objects.get(is_current=True)
    next_week: Week = Week.objects.get_next(current_season)

    if not next_week:
        return
    right_now = pytz.timezone("US/Pacific").localize(datetime.datetime.now())
    time_diff = (next_week.lock_datetime - right_now).total_seconds()
    due_in = get_pretty_time(time_diff)

    recipients = list(PlayerStatus.objects.for_email_reminders(next_week))
    phone_numbers = list(PlayerStatus.objects.for_phone_reminders(next_week))

    subject = "Survivor Picks Reminder"
    message = f"Week {next_week.week_num} pick due in:\n\n{due_in}!"
    if recipients:
        send_email_task.delay(subject, recipients, message)

    client = Client(settings.TWILIO_SID, settings.TWILIO_KEY)

    for phone_number in phone_numbers:
        client.messages.create(
            to=phone_number,
            from_=settings.TWILIO_NUM,
            body=f"Survivor Picks Reminder!\n{message}",
        )


@app.task()
def send_email_task(subject, recipients, message):
    import smtplib

    from email.mime.text import MIMEText

    from fbsurvivor import settings

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


@app.task()
def update_board_cache():
    from core.helpers import update_league_caches

    update_league_caches()
