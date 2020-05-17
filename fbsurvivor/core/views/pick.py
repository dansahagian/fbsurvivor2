from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from fbsurvivor.core.forms import PickForm
from fbsurvivor.core.models import Player, Season, PlayerStatus, Pick, Week, Team


def get_player_info_and_context(link, year):
    player = get_object_or_404(Player, link=link)
    season = get_object_or_404(Season, year=year)
    player_status = get_object_or_404(PlayerStatus, player=player, season=season)
    context = {
        "player": player,
        "season": season,
        "player_status": player_status,
    }

    return player, season, player_status, context


def picks(request, link, year):
    player, season, player_status, context = get_player_info_and_context(link, year)
    context["picks"] = Pick.objects.for_player_season(player, season)
    if player_status.is_retired:
        messages.info(request, "Reminder: You retired!")

    return render(request, "picks.html", context=context)


def pick(request, link, year, week):
    player, season, player_status, context = get_player_info_and_context(link, year)
    week = get_object_or_404(Week, season=season, week_num=week)

    if week.is_locked:
        messages.warning(request, f"Week {week.week_num} is locked!")
        return redirect(reverse("picks", args=[link, year]))

    user_pick = get_object_or_404(Pick, player=player, week=week)
    context["pick"] = user_pick

    if request.method == "GET":
        form = PickForm(player, season, week)
        context["form"] = form
        return render(request, "pick.html", context=context)

    if request.method == "POST":
        form = PickForm(player, season, week, request.POST)

        if form.is_valid():
            team_code = form.cleaned_data["team"]

            if team_code:
                choice = get_object_or_404(Team, team_code=team_code, season=season)
                user_pick.team = choice
            else:
                user_pick.team = None

            user_pick.save()
            team_code = user_pick.team.team_code if user_pick.team else "No team "
            messages.success(
                request, f"{team_code} submitted for week {week.week_num}",
            )

        else:
            messages.warning(request, "Bad form submission")

        return redirect(reverse("picks", args=[link, year]))
