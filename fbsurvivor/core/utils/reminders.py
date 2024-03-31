from fbsurvivor.core.models import PlayerStatus, Season, Week
from fbsurvivor.core.utils.deadlines import get_reminder_message
from fbsurvivor.core.utils.emails import send_email


def send_reminders():
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
        send_email(subject, email_recipients, message)
