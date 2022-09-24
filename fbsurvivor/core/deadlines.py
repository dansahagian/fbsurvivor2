import arrow

from fbsurvivor.core.models import Week, Lock, PlayerStatus, Season, Pick


def _zero_pad_number(number):
    return str(int(number)).zfill(2)


def get_countdown(deadline):
    if not deadline:
        return None

    right_now = arrow.now()

    seconds = (deadline - right_now).total_seconds()
    if seconds <= 0:
        return None

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, remainder = divmod(remainder, 60)

    d = "day" if days == 1 else "days"
    h = "hour" if hours == 1 else "hours"
    m = "minute" if minutes == 1 else "minutes"

    days = f"{int(days)} {d}" if days else ""
    hours = f"{int(hours)} {h}" if hours else ""
    minutes = f"{int(minutes)} {m}" if minutes else ""

    if days and hours and minutes:
        return f"{days}, {hours}, & {minutes}"
    elif days and (hours or minutes):
        return f"{days} & {hours}{minutes}"
    elif hours and minutes:
        return f"{hours} & {minutes}"
    else:
        return f"{hours}{minutes}"


def get_early_deadline(season, next_week):
    now = arrow.now().datetime
    try:
        deadline = (
            Lock.objects.filter(
                week__season=season, week=next_week, lock_datetime__gte=now
            )
            .order_by("lock_datetime")
            .first()
        )
    except Lock.DoesNotExist:
        deadline = None

    return deadline.lock_datetime if deadline else None


def get_weekly_deadline(season, next_week):
    try:
        deadline = Week.objects.get(season=season, week_num=next_week.week_num)
    except Week.DoesNotExist:
        deadline = None

    return deadline.lock_datetime if deadline else None


def get_next_deadline(season):
    next_week: Week = Week.objects.get_next(season)
    if not next_week:
        return None

    early = get_early_deadline(season, next_week)
    weekly = get_weekly_deadline(season, next_week)

    return get_countdown(early) or get_countdown(weekly)


def get_picks_count_display(season: Season) -> str | None:
    next_week: Week = Week.objects.get_next(season)
    if not next_week:
        return None

    player_count = PlayerStatus.objects.filter(season=season, is_retired=False).count()
    pick_count = Pick.objects.filter(week=next_week, team__isnull=False).count()

    return f"{pick_count} / {player_count} active players have picked this week."
