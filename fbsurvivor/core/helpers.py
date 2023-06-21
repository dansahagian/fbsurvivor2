from uuid import uuid4

import redis
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from fbsurvivor.core.models.pick import Pick
from fbsurvivor.core.models.player import Player, PlayerStatus, League
from fbsurvivor.core.models.season import Season


def get_player_context(player: Player, year: int):
    season = get_object_or_404(Season, year=year)

    try:
        player_status = PlayerStatus.objects.get(player=player, season=season)
    except PlayerStatus.DoesNotExist:
        player_status = None

    context = {"player": player, "season": season, "player_status": player_status}

    return season, player_status, context


def get_current_season():
    return Season.objects.get(is_current=True)


def send_to_latest_season_played(request):
    username = request.session.get("username")
    ps = PlayerStatus.objects.filter(player__username=username).order_by("-season__year")
    if ps:
        latest = ps[0].season.year
        messages.info(request, f"No record for the requested year. Here is {latest}")
        return redirect(reverse("board", args=[latest]))
    else:
        messages.info(request, "We don't have a record of you playing any season.")
        return redirect(reverse("signin"))


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


def _get_board(season, league):
    ps = PlayerStatus.objects.for_season_board(season, league).prefetch_related("player")
    board = [
        (x, list(Pick.objects.for_board(x.player, season).select_related("team"))) for x in ps
    ]

    return ps, board


def get_board(season, league, overwrite_cache=False):
    if overwrite_cache:
        player_statuses, board = _get_board(season, league)
        try:
            cache.set(f"player_statuses_{season.year}_{league}", player_statuses, timeout=None)
            cache.set(f"board_{season.year}_{league}", board, timeout=None)
            print("Caching board")
        except redis.ConnectionError:
            print("Redis is unavailable. Could not cache board.")
        return player_statuses, board

    try:
        player_statuses = cache.get(f"player_statuses_{season.year}_{league}")
        board = cache.get(f"board_{season.year}_{league}")
        if not (player_statuses and board):
            return get_board(season, league, overwrite_cache=True)
        print("Using cached board.")
        return player_statuses, board
    except redis.ConnectionError:
        print("Redis is unavailable. Could not cache board.")
        return _get_board(season, league)


def update_league_caches(season=None):
    if not season:
        season = Season.objects.get(is_current=True)
    leagues = League.objects.all()
    for league in leagues:
        get_board(season, league, overwrite_cache=True)


def generate_ntfy_topic():
    ntfy_topic = str(uuid4())
    ntfy_topics = Player.objects.values_list("ntfy_topic", flat=True)

    if ntfy_topic in ntfy_topics:
        return generate_ntfy_topic()
    return ntfy_topic
