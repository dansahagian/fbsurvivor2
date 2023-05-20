from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from fbsurvivor.celery import send_email_task
from fbsurvivor.core.deadlines import get_next_deadline, get_picks_count_display
from fbsurvivor.core.forms import EmailForm
from fbsurvivor.core.helpers import (
    get_board,
    get_current_season,
    get_player,
    get_player_status_info,
    send_to_latest_season_played,
)
from fbsurvivor.core.models.pick import Pick
from fbsurvivor.core.models.player import generate_link, Player, PlayerStatus, Payout
from fbsurvivor.core.models.season import Season
from fbsurvivor.core.models.week import Week
from fbsurvivor.settings import DOMAIN, VENMO


def signin(request):
    if request.method == "GET":
        context = {
            "form": EmailForm(),
        }
        return render(request, "signin.html", context=context)

    if request.method == "POST":
        form = EmailForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                player = Player.objects.get(email=email)
            except Player.DoesNotExist:
                player = None

            if player:
                subject = "Survivor - Sign in"
                message = f"Click the link below to signin\n{DOMAIN}/login/{player.link}"
                send_email_task.delay(subject, [email], message)
        return render(request, "signin-sent.html")


def login(request, link):
    player = get_object_or_404(Player, link=link)
    current_season = get_object_or_404(Season, is_current=True)

    request.session["link"] = player.link
    return redirect(reverse("board", args=[current_season.year]))


def board_redirect(request):
    get_player(request)
    season = get_current_season()

    return redirect(reverse("board", args=[season.year]))


def board(request, year):
    player = get_player(request)
    season, player_status = get_player_status_info(player, year)

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

    context = {
        "player": player,
        "season": season,
        "player_status": player_status,
        "can_play": can_play,
        "weeks": weeks,
        "board": leader_board,
        "player_count": player_statuses.count(),
        "survivor": survivor,
        "deadline": deadline,
        "picks_display": picks_display,
        "playable": playable,
        "venmo": VENMO,
    }

    return render(request, "board.html", context=context)


def play(request, year):
    player = get_player(request)
    season, player_status = get_player_status_info(player, year)

    if player_status:
        messages.info(request, f"You are already playing for {year}!")
        return redirect(reverse("board", args=[year]))

    if season.is_locked:
        return send_to_latest_season_played(request)

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
        messages.info(request, f"Good luck in the {year} season!")
        return redirect(reverse("board", args=[year]))


def retire(request, year):
    player = get_player(request)
    season, player_status = get_player_status_info(player, year)

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


def reset_link(request):
    player = get_player(request)

    old_links = player.old_links.split(",")
    old_links.append(str(player.link))

    player.old_links = ",".join(old_links)
    player.link = generate_link()
    player.save()

    messages.info(request, "Link Updated. Please check your email!")
    return redirect(reverse("login", args=[player.link]))


def payouts(request):
    player = get_player(request)
    player_payouts = Payout.objects.for_payout_table(player.league)

    context = {"player": player, "payouts": player_payouts, "season": get_current_season()}

    return render(request, "payouts.html", context=context)


def rules(request):
    player = get_player(request)

    context = {"player": player, "season": get_current_season()}

    return render(request, "rules.html", context=context)


def seasons(request):
    player = get_player(request)

    years = list(PlayerStatus.objects.player_years(player))

    context = {"player": player, "years": years, "season": get_current_season()}

    return render(request, "seasons.html", context=context)


def dark_mode(request):
    link = request.session.get("link")
    player = get_object_or_404(Player, link=link)
    player.is_dark_mode = not player.is_dark_mode
    player.save()
    return redirect(request.session["path"])
