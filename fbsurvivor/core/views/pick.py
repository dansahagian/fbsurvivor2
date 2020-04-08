from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from fbsurvivor.core.models import Player, Season, PlayerStatus, Pick


def picks_view(request, link, year):
    player = get_object_or_404(Player, link=link)
    season = get_object_or_404(Season, year=year)
    ps = get_object_or_404(PlayerStatus, player=player, season=season)

    picks = Pick.objects.filter(player=player, week__season=season)
    context = {
        "player": player,
        "season": season,
        "player_status": ps,
        "picks": picks,
    }
    return render(request, "picks-page.html", context=context)
