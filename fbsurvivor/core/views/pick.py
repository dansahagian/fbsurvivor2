from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from fbsurvivor.core.forms import PickForm
from fbsurvivor.core.helpers import (
    get_current_season,
    get_player_context,
)
from fbsurvivor.core.models.pick import Pick
from fbsurvivor.core.models.team import Team
from fbsurvivor.core.models.week import Week
from fbsurvivor.core.views.auth import authenticate_player


@authenticate_player
def picks_redirect(request):
    season = get_current_season()

    return redirect(reverse("picks", args=[season.year]))


@authenticate_player
def picks(request, year, **kwargs):
    player = kwargs["player"]
    season, player_status, context = get_player_context(player, year)

    can_retire = player_status and (not player_status.is_retired) and season.is_current

    context["picks"] = (
        Pick.objects.for_player_season(player, season)
        .prefetch_related("week")
        .prefetch_related("team")
    )
    context["status"] = "Retired" if player_status.is_retired else "Playing"
    context["can_retire"] = can_retire
    context["current"] = "picks"

    return render(request, "picks.html", context=context)


@authenticate_player
def pick(request, year, week, **kwargs):
    player = kwargs["player"]
    season, player_status, context = get_player_context(player, year)

    week = get_object_or_404(Week, season=season, week_num=week)

    user_pick = get_object_or_404(Pick, player=player, week=week)
    context["pick"] = user_pick

    if user_pick.is_locked:
        messages.info(request, f"Week {week.week_num} is locked!")
        return redirect(reverse("picks", args=[year]))

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
                if user_pick.is_locked:
                    messages.info(request, f"Week {week.week_num} is locked!")
                    return redirect(reverse("picks", args=[year]))
            else:
                user_pick.team = None

            user_pick.save()
            team_code = user_pick.team.team_code if user_pick.team else "No team "
            messages.info(
                request,
                f"{team_code} submitted for week {week.week_num}",
            )

        else:
            messages.info(request, "Bad form submission")

        return redirect(reverse("picks", args=[year]))
