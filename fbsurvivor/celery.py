from celery import Celery

from fbsurvivor.settings import BROKER_URL

app = Celery("fbsurvivor", broker=BROKER_URL)


@app.task()
def send_reminders_task():
    from fbsurvivor.core.models.player import PlayerStatus
    from fbsurvivor.core.models.season import Season
    from fbsurvivor.core.models.week import Week
    from fbsurvivor.core.deadlines import get_reminder_message

    current_season: Season = Season.objects.get(is_current=True)
    next_week: Week = Week.objects.get_next(current_season)

    if not next_week:
        return

    message = get_reminder_message(current_season, next_week)

    if not message:
        return

    subject = f"Survivor Week {next_week.week_num} Reminder"
    message = f"Survivor Week {next_week.week_num} Reminder\n\n" + message

    recipients = list(PlayerStatus.objects.for_email_reminders(next_week))
    phone_numbers = list(PlayerStatus.objects.for_phone_reminders(next_week))

    if recipients:
        send_email_task.delay(subject, recipients, message)

    for phone_number in phone_numbers:
        send_text_task.delay(phone_number, message)


@app.task()
def send_email_task(subject, recipients, message):
    import smtplib

    from email.mime.text import MIMEText

    from fbsurvivor import settings

    if settings.ENV == "dev":
        print(f"\n\ndev - sending email\n{message}\n\n")
        return

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
def send_text_task(phone_number, message):
    from twilio.rest import Client

    from fbsurvivor import settings

    if settings.ENV == "dev":
        print(f"\n\ndev - sending text\n{message}\n\n")
        return

    client = Client(settings.TWILIO_SID, settings.TWILIO_KEY)

    client.messages.create(
        to=phone_number,
        from_=settings.TWILIO_NUM,
        body=message,
    )


@app.task()
def update_board_cache():
    from fbsurvivor.core.helpers import update_league_caches

    update_league_caches()
