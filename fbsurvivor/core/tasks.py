from twilio.rest import Client

from fbsurvivor import settings
from fbsurvivor.core.models import PlayerStatus, Season, Pick, Week, Player
from fbsurvivor.core.utils import get_localized_right_now, send_email, get_pretty_time


def update_player_records(year):
    try:
        season = Season.objects.get(year=year)
        player_statuses = PlayerStatus.objects.filter(season=season)
        updates = [update_record(ps) for ps in player_statuses]
        return len(updates)
    except Season.DoesNotExist:
        return 0


def update_record(player_status):
    player = player_status.player
    season = player_status.season

    picks = Pick.objects.filter(player=player, week__season=season)
    player_status.win_count = picks.filter(result="W").count()
    player_status.loss_count = picks.filter(result="L").count()
    player_status.save()
    return True


def send_reminders():
    current_season: Season = Season.objects.get(is_current=True)
    next_week: Week = Week.objects.get_next(current_season)

    if not next_week:
        return

    time_diff = (next_week.lock_datetime - get_localized_right_now()).total_seconds()
    due_in = get_pretty_time(time_diff)

    recipients = list(Player.objects.for_email_reminders(next_week))
    phone_numbers = list(Player.objects.for_phone_reminders(next_week))

    subject = "Survivor Picks Reminder"
    message = f"Week {next_week.week_num} pick due in:\n\n{due_in}!"
    if recipients:
        send_email(subject, recipients, message)

    client = Client(settings.TWILIO_SID, settings.TWILIO_KEY)

    for phone_number in phone_numbers:
        client.messages.create(
            to=phone_number,
            from_=settings.TWILIO_NUM,
            body=f"Survivor Picks Reminder!\n{message}",
        )
