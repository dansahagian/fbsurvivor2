from celery import Celery

app = Celery("fbsurvivor")


@app.task()
def send_reminders_task():
    from fbsurvivor.core.tasks import send_reminders

    send_reminders()


@app.task()
def send_email_task(subject, recipients, message):
    from fbsurvivor.core.tasks import send_email

    send_email(subject, recipients, message)
