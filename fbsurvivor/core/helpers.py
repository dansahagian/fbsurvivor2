from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from fbsurvivor.core.models import Player, Season, PlayerStatus


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
