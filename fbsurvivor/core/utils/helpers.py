from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from fbsurvivor.core.models import League, Player, PlayerStatus, Season, Pick


def get_player_context(player: Player, year: int):
    season = get_object_or_404(Season, year=year)
    current_season = get_current_season()

    try:
        player_status = PlayerStatus.objects.get(player=player, season=season)
    except PlayerStatus.DoesNotExist:
        player_status = None

    context = {
        "player": player,
        "season": season,
        "player_status": player_status,
        "current_season": current_season,
    }

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


def get_board(season, league):
    ps = PlayerStatus.objects.for_season_board(season, league).prefetch_related("player")
    board = [
        (x, list(Pick.objects.for_board(x.player, season).select_related("team"))) for x in ps
    ]

    return ps, board


def update_league_caches(season=None):
    if not season:
        season = Season.objects.get(is_current=True)
    leagues = League.objects.all()
    for league in leagues:
        get_board(season, league, overwrite_cache=True)
