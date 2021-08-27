from celery import Celery

from fbsurvivor.settings import BROKER_URL

app = Celery("fbsurvivor", broker=BROKER_URL)


@app.task()
def send_reminders_task():
    import arrow

    from twilio.rest import Client

    from fbsurvivor import settings
    from fbsurvivor.core.models import PlayerStatus, Season, Week, Lock
    from fbsurvivor.core.helpers import get_pretty_time

    current_season: Season = Season.objects.get(is_current=True)
    next_week: Week = Week.objects.get_next(current_season)

    if not next_week:
        return
    right_now = arrow.now()
    early_lock = Lock.objects.filter(week=next_week).order_by("lock_datetime").first()

    subject = "Survivor Picks Reminder"
    message = f"Week {next_week.week_num} reminders\n\n"

    if early_lock:
        early_diff = (early_lock.lock_datetime - right_now).total_seconds()
        if early_diff > 0:
            early_due_in = get_pretty_time(early_diff)
            message += f"Early picks lock in: {early_due_in}\n\n"

    weekly_diff = (next_week.lock_datetime - right_now).total_seconds()
    weekly_due_in = get_pretty_time(weekly_diff)

    message += f"Weekly picks lock in: {weekly_due_in}"

    recipients = list(PlayerStatus.objects.for_email_reminders(next_week))
    phone_numbers = list(PlayerStatus.objects.for_phone_reminders(next_week))

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
