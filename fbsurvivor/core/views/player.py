from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse

from fbsurvivor.celery import send_push_notification
from fbsurvivor.core.deadlines import get_next_deadline, get_picks_count_display
from fbsurvivor.core.helpers import (
    get_board,
    get_current_season,
    get_player_context,
    send_to_latest_season_played,
    generate_ntfy_topic,
)
from fbsurvivor.core.models.pick import Pick
from fbsurvivor.core.models.player import PlayerStatus, Payout, Player
from fbsurvivor.core.models.season import Season
from fbsurvivor.core.models.week import Week
from fbsurvivor.core.views.auth import authenticate_player
from fbsurvivor.settings import VENMO, CONTACT


@authenticate_player
def board_redirect(request, **kwargs):
    season = get_current_season()

    return redirect(reverse("board", args=[season.year]))


@authenticate_player
def board(request, year, **kwargs):
    player = kwargs["player"]
    season, player_status, context = get_player_context(player, year)

    if season.is_locked and not player_status:
        return send_to_latest_season_played(request)

    can_play = not player_status and season.is_current and not season.is_locked
    weeks = Week.objects.for_display(season).values_list("week_num", flat=True)
    player_statuses, leader_board = get_board(season, player.league)
    survivors = player_statuses.filter(is_survivor=True)

    try:
        playable = Season.objects.get(is_current=True, is_locked=False).year
    except Season.DoesNotExist:
        playable = None

    deadline = get_next_deadline(season)
    picks_display = get_picks_count_display(season)

    survivor = survivors[0].player.username if len(survivors) == 1 else ""

    context.update(
        {
            "can_play": can_play,
            "weeks": weeks,
            "board": leader_board,
            "player_count": player_statuses.count(),
            "survivor": survivor,
            "deadline": deadline,
            "picks_display": picks_display,
            "playable": playable,
            "venmo": VENMO,
            "show_footer": True,
        }
    )

    return render(request, "board.html", context=context)


@authenticate_player
def play(request, year, **kwargs):
    player = kwargs["player"]
    season, player_status, context = get_player_context(player, year)

    if player_status:
        messages.info(request, f"You are already playing for {year}!")
        return redirect(reverse("board", args=[year]))

    if season.is_locked:
        return send_to_latest_season_played(request)

    context.update(
        {
            "player": player,
            "season": season,
        }
    )

    if request.method == "GET":
        return render(request, "confirm.html", context=context)

    if request.method == "POST":
        PlayerStatus.objects.create(player=player, season=season)
        weeks = Week.objects.filter(season=season)
        picks = [Pick(player=player, week=week) for week in weeks]
        Pick.objects.bulk_create(picks)
        get_board(season, player.league, overwrite_cache=True)
        messages.info(request, f"Good luck in the {year} season!")

        topic = Player.objects.get(username="DanTheAutomator").ntfy_topic
        send_push_notification.delay(topic, "New Player!", f"{player.username} is playing!")

        return redirect(reverse("board", args=[year]))


@authenticate_player
def retire(request, year, **kwargs):
    player = kwargs["player"]
    season, player_status, context = get_player_context(player, year)

    if not player_status:
        messages.info(request, "You can NOT retire from a season you didn't play!")
    elif player_status.is_retired:
        messages.info(request, f"You already retired in {year}!")
    elif not season.is_current:
        messages.info(request, "You can NOT retire from a past season!")
    else:
        player_status.is_retired = True
        player_status.save()
        Pick.objects.filter(player=player, week__season=season, result__isnull=True).update(
            result="R"
        )
        get_board(season, player.league, overwrite_cache=True)
        messages.info(request, "You have retired. See you next year!")

    return redirect(reverse("board", args=[year]))


@authenticate_player
def payouts(request, **kwargs):
    player = kwargs["player"]
    player_payouts = Payout.objects.for_payout_table(player.league)

    context = {"player": player, "payouts": player_payouts, "season": get_current_season()}

    return render(request, "payouts.html", context=context)


@authenticate_player
def rules(request, **kwargs):
    player = kwargs["player"]

    context = {"player": player, "season": get_current_season(), "contact": CONTACT}

    return render(request, "rules.html", context=context)


@authenticate_player
def seasons(request, **kwargs):
    player = kwargs["player"]

    years = list(PlayerStatus.objects.player_years(player))

    context = {"player": player, "years": years, "season": get_current_season()}

    return render(request, "seasons.html", context=context)


@authenticate_player
def dark_mode(request, **kwargs):
    player = kwargs["player"]
    player.is_dark_mode = not player.is_dark_mode
    player.save()

    return redirect(kwargs["path"])


@authenticate_player
def reminders(request, **kwargs):
    player = kwargs["player"]
    context = {"player": player, "season": get_current_season(), "contact": CONTACT}

    return render(request, "reminders.html", context=context)


@authenticate_player
def change_reminders(request, **kwargs):
    player = kwargs["player"]

    if not player.has_push_reminders:
        player.has_push_reminders = True
        if not player.ntfy_topic:
            player.ntfy_topic = generate_ntfy_topic()

        send_push_notification.delay(
            player.ntfy_topic,
            "Survivor Push Notifications",
            "You've enabled push notifications for Survivor.",
        )
    else:
        player.has_push_reminders = False
    player.save()

    return redirect(reverse("reminders"))
