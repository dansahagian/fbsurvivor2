from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from fbsurvivor.core.forms import PickForm
from fbsurvivor.core.models import Player, Season, PlayerStatus, Pick, Week, Team


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


def pick_view(request, link, year, week):
    player = get_object_or_404(Player, link=link)
    season = get_object_or_404(Season, year=year)
    week = get_object_or_404(Week, season=season, week_num=week)
    ps = get_object_or_404(PlayerStatus, player=player, season=season)

    pick = get_object_or_404(Pick, player=player, week=week)

    if week.is_locked:
        messages.warning(request, f"Week {week.week_num} is locked!")
        return redirect(reverse("picks_view", args=[link, year]))

    context = {
        "player": player,
        "season": season,
        "pick": pick,
    }

    if request.method == "GET":
        form = PickForm(player, season, week)
        context["form"] = form
        return render(request, "pick-page.html", context=context)

    if request.method == "POST":
        form = PickForm(player, season, week, request.POST)

        if form.is_valid():
            team_code = form.cleaned_data["team"]
            pick.team = Team.objects.get(team_code=team_code, season=season)
            pick.save()
            messages.success(
                request, f"{pick.team.team_code} submitted for week {week.week_num}"
            )
            return redirect(reverse("picks_view", args=[link, year]))
