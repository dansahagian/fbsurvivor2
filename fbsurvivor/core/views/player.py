from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from fbsurvivor.core.helpers import (
    get_player_info,
    send_to_latest_season_played,
    cache_board,
)
from fbsurvivor.core.models import Season, Player, PlayerStatus, Pick, Week, Payout


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

    player_statuses = cache.get(f"player_statuses_{year}")
    board = cache.get(f"board_{year}")

    if not (player_statuses and board):
        player_statuses = PlayerStatus.objects.for_season_board(
            season
        ).prefetch_related("player")

        board = [
            (x, list(Pick.objects.for_board(x.player, season).select_related("team")))
            for x in player_statuses
        ]

    survivors = player_statuses.filter(is_survivor=True)
    if len(survivors) == 1:
        survivor = survivors[0].player.username
    else:
        survivor = ""

    context = {
        "player": player,
        "season": season,
        "player_status": player_status,
        "can_play": can_play,
        "can_retire": can_retire,
        "weeks": weeks,
        "board": board,
        "player_count": player_statuses.count(),
        "survivor": survivor,
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
        cache_board(season)
        messages.success(request, f"Congrats on joining the {year} league. Good luck!")
        return redirect(reverse("player", args=[link, year]))


def retire(request, link, year):
    player, season, player_status = get_player_info(link, year)

    if not player_status:
        messages.info(request, "You can NOT retire from a season you didn't play!")
    elif player_status.is_retired:
        messages.info(request, f"You already retired in {year}!")
    elif not season.is_current:
        messages.info(request, f"You can NOT retire from a past season!")
    else:
        player_status.is_retired = True
        player_status.save()
        Pick.objects.filter(
            player=player, week__season=season, result__isnull=True
        ).update(result="R")
        cache_board(season)
        messages.success(request, f"You have retired. See you next year!")

    return redirect(reverse("player", args=[link, year]))


def other(request, link, year):
    player = get_object_or_404(Player, link=link)
    season = get_object_or_404(Season, year=year)
    years = PlayerStatus.objects.player_years(player)

    player_payouts = Payout.objects.for_payout_table()

    context = {
        "player": player,
        "season": season,
        "years": years,
        "payouts": player_payouts,
    }

    return render(request, "other.html", context=context)
