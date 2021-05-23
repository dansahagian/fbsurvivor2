import redis
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from fbsurvivor.core.models import Player, Season, PlayerStatus, Pick


def get_player_info(link, year):
    player = get_object_or_404(Player, link=link)
    season = get_object_or_404(Season, year=year)

    try:
        player_status = PlayerStatus.objects.get(player=player, season=season)
    except PlayerStatus.DoesNotExist:
        player_status = None

    return player, season, player_status


def send_to_latest_season_played(request, link, year):
    ps = PlayerStatus.objects.filter(player__link=link).order_by("-season__year")
    if ps:
        latest = ps[0].season.year
        messages.warning(request, f"You did NOT play in {year}. Here is {latest}")
        return redirect(reverse("player", args=[link, latest]))
    else:
        messages.warning(request, f"We don't have a record of you playing any season.")
        return redirect(reverse("home"))


def get_pretty_time(seconds):
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


def _get_board(season):
    ps = PlayerStatus.objects.for_season_board(season).prefetch_related("player")
    board = [
        (x, list(Pick.objects.for_board(x.player, season).select_related("team")))
        for x in ps
    ]

    return ps, board


def get_board(season, overwrite_cache=False):
    if overwrite_cache:
        player_statuses, board = _get_board(season)
        try:
            cache.set(f"player_statuses_{season.year}", player_statuses, timeout=None)
            cache.set(f"board_{season.year}", board, timeout=None)
            print("Caching board")
        except redis.ConnectionError:
            print("Redis is unavailable. Could not cache board.")
        return player_statuses, board

    try:
        player_statuses = cache.get(f"player_statuses_{season.year}")
        board = cache.get(f"board_{season.year}")
        if not (player_statuses and board):
            return get_board(season, overwrite_cache=True)
        print("Using cached board.")
        return player_statuses, board
    except redis.ConnectionError:
        print("Redis is unavailable. Could not cache board.")
        return _get_board(season)
