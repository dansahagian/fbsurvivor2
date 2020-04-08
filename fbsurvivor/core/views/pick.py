from django.shortcuts import render, get_object_or_404

from fbsurvivor.core.models import Player, Season


def picks_view(request, link, year):
    player = get_object_or_404(Player, link=link)
    season = get_object_or_404(Season, year=year)


