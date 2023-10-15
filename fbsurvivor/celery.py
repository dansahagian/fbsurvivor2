from celery import Celery

from fbsurvivor.settings import BROKER_URL

app = Celery("fbsurvivor", broker=BROKER_URL)


@app.task()
def send_reminders_task():
    from fbsurvivor.core.models import PlayerStatus
    from fbsurvivor.core.models import Season
    from fbsurvivor.core.models import Week
    from fbsurvivor.core.utils.deadlines import get_reminder_message

    current_season: Season = Season.objects.get(is_current=True)
    next_week: Week = Week.objects.get_next(current_season)

    if not next_week:
        return

    message = get_reminder_message(current_season, next_week)

    if not message:
        return

    subject = f"🏈 Survivor Week {next_week.week_num} Reminder"
    message = f"Week {next_week.week_num} Locks:\n\n" + message

    if email_recipients := list(PlayerStatus.objects.for_email_reminders(next_week)):
        send_email_task.delay(subject, email_recipients, message)


@app.task()
def send_email_task(subject, recipients, message):
    import smtplib

    from email.mime.text import MIMEText

    from fbsurvivor.settings import ENV, SMTP_SENDER, SMTP_USER, SMTP_PASSWORD, SMTP_SERVER

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


@app.task()
def update_board_cache():
    from fbsurvivor.core.utils.helpers import update_league_caches

    update_league_caches()
