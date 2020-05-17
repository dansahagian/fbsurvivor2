from celery import Celery

app = Celery("fbsurvivor")


@app.task()
def send_reminders_task():
    from fbsurvivor.core.tasks import send_reminders

    send_reminders()
