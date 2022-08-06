from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from fbsurvivor.core.deadlines import get_next_deadline
from fbsurvivor.core.helpers import (
    get_board,
    get_player_info,
    send_to_latest_season_played,
)
from fbsurvivor.core.models import (
    Season,
    Player,
    PlayerStatus,
    Pick,
    Week,
    Payout,
)
from fbsurvivor.settings import VENMO


def dark_mode(request, link):
    player = get_object_or_404(Player, link=link)
    player.is_dark_mode = not player.is_dark_mode
    player.save()
    return redirect(reverse("more", args=[link]))


def player_redirect(request, link):
    get_object_or_404(Player, link=link)
    current_season = get_object_or_404(Season, is_current=True)
    return redirect(reverse("player", args=[link, current_season.year]))


def player(request, link, year):
    player, season, player_status = get_player_info(link, year)

    if season.is_locked and not player_status:
        return send_to_latest_season_played(request, link, year)

    can_play = not player_status and season.is_current and not season.is_locked
    weeks = Week.objects.for_display(season).values_list("week_num", flat=True)
    player_statuses, board = get_board(season, player.league)
    survivors = player_statuses.filter(is_survivor=True)

    try:
        playable = Season.objects.get(is_current=True, is_locked=False).year
    except Season.DoesNotExist:
        playable = None

    deadline = get_next_deadline(season)

    survivor = survivors[0].player.username if len(survivors) == 1 else ""

    if player_status and not player_status.is_paid:
        messages.info(request, f"Unpaid - Venmo $30 to {VENMO}")

    context = {
        "player": player,
        "season": season,
        "player_status": player_status,
        "can_play": can_play,
        "weeks": weeks,
        "board": board,
        "player_count": player_statuses.count(),
        "survivor": survivor,
        "deadline": deadline,
        "playable": playable,
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
        return render(request, "confirm.html", context=context)

    if request.method == "POST":
        PlayerStatus.objects.create(player=player, season=season)
        weeks = Week.objects.filter(season=season)
        picks = [Pick(player=player, week=week) for week in weeks]
        Pick.objects.bulk_create(picks)
        get_board(season, player.league, overwrite_cache=True)
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
        get_board(season, player.league, overwrite_cache=True)
        messages.success(request, f"You have retired. See you next year!")

    return redirect(reverse("player", args=[link, year]))


def more(request, link):
    player = get_object_or_404(Player, link=link)

    years = list(PlayerStatus.objects.player_years(player))

    context = {"player": player, "years": years}

    return render(request, "more.html", context=context)


def payouts(request, link):
    player = get_object_or_404(Player, link=link)

    player_payouts = Payout.objects.for_payout_table(player.league)

    context = {
        "player": player,
        "payouts": player_payouts,
    }

    return render(request, "payouts.html", context=context)


def rules(request, link):
    player = get_object_or_404(Player, link=link)

    context = {
        "player": player,
    }
    return render(request, "rules.html", context=context)
