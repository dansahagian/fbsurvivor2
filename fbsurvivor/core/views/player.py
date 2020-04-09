from django.contrib import messages
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from fbsurvivor.core.models import Season, Player, PlayerStatus, Pick, Week
from fbsurvivor.core.utils import get_player_info, send_to_latest_season_played


def player_redirect(request, link):
    get_object_or_404(Player, link=link)
    current_season = get_object_or_404(Season, is_current=True)
    return redirect(reverse("player", args=[link, current_season.year]))


def player(request, link, year):
    player, season, player_status = get_player_info(link, year)

    if season.is_locked and not player_status:
        return send_to_latest_season_played(request, link, year)

    can_retire = player_status and (not player_status.is_retired) and season.is_current
    can_play = not player_status and season.is_current and not season.is_locked
    weeks = Week.objects.for_display(season).values_list("week_num", flat=True)
    years = (
        PlayerStatus.objects.filter(player=player)
        .values_list("season__year", flat=True)
        .order_by("season__year")
    )

    player_statuses = (
        PlayerStatus.objects.filter(season=season)
        .annotate(lower=Lower("player__username"))
        .order_by("-is_survivor", "is_retired", "-win_count", "loss_count", "lower",)
    )

    board = [
        (ps, list(Pick.objects.for_player_season(ps.player, season)))
        for ps in player_statuses
    ]

    context = {
        "player": player,
        "season": season,
        "player_status": player_status,
        "can_play": can_play,
        "can_retire": can_retire,
        "weeks": weeks,
        "years": years,
        "board": board,
        "player_count": player_statuses.count(),
    }

    return render(request, "player.html", context=context)


def play(request, link, year):
    player, season, player_status = get_player_info(link, year)

    if player_status:
        messages.info(request, f"You are already playing for {year}!")
        return redirect(reverse("player", args=[link, year]))

    if season.is_locked:
        return send_to_latest_season_played(request, link, year)

    context = {
        "player": player,
        "season": season,
    }

    if request.method == "GET":
        return render(request, "rules.html", context=context)

    if request.method == "POST":
        PlayerStatus.objects.create(player=player, season=season)
        weeks = Week.objects.filter(season=season)
        picks = [Pick(player=player, week=week) for week in weeks]
        Pick.objects.bulk_create(picks)
        messages.success(request, f"Congrats on joining the {year} league. Good luck!")
        return redirect(reverse("player", args=[link, year]))
