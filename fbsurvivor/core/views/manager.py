import secrets
import string

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from fbsurvivor.celery import send_reminders_task
from fbsurvivor.core.helpers import update_player_records, cache_board
from fbsurvivor.core.models import Player, Season, PlayerStatus, Week, Pick, Team


def get_admin_info(link, year):
    player = get_object_or_404(Player, link=link, is_admin=True)
    season = get_object_or_404(Season, year=year)
    context = {"player": player, "season": season}
    return player, season, context


def manager(request, link, year):
    player, season, context = get_admin_info(link, year)
    return render(request, "manager.html", context=context)


def paid(request, link, year):
    player, season, context = get_admin_info(link, year)
    player_statuses = PlayerStatus.objects.paid_for_season(season).prefetch_related(
        "player"
    )
    context["player_statuses"] = player_statuses
    return render(request, "paid.html", context=context)


def user_paid(request, link, year, user_link):
    player, season, context = get_admin_info(link, year)
    ps = get_object_or_404(PlayerStatus, player__link=user_link, season=season)
    ps.is_paid = True
    ps.save()
    cache_board(season)
    messages.success(request, f"{ps.player.username} marked as paid!")
    return redirect(reverse("paid", args=[link, year]))


def results(request, link, year):
    player, season, context = get_admin_info(link, year)
    current_week = Week.objects.get_current(season)
    teams = Pick.objects.for_results(current_week)

    context["week"] = current_week
    context["teams"] = teams

    return render(request, "results.html", context=context)


def mark_result(request, link, year, week, team, result):
    player, season, context = get_admin_info(link, year)
    week = get_object_or_404(Week, season=season, week_num=week)

    team = get_object_or_404(Team, team_code=team, season=season)
    Pick.objects.for_result_updates(week, team).update(result=result)
    Pick.objects.for_no_picks(week).update(result="L")

    messages.success(request, f"Picks for week {week.week_num} of {team} updated!")

    player_records_updated = update_player_records(year)
    cache_board(season)
    messages.success(request, f"{player_records_updated} player records updated!")

    return redirect(reverse("results", args=[link, year]))


def remind(request, link, year):
    get_object_or_404(Player, link=link, is_admin=True)
    send_reminders_task.delay()
    messages.success(request, f"Reminder task kicked off")
    return redirect(reverse("manager", args=[link, year]))


def get_link(request, link):
    get_object_or_404(Player, link=link, is_admin=True)
    char_set = string.ascii_lowercase + string.digits
    links = Player.objects.values_list("link", flat=True)
    do = True

    while link in links or do:
        do = False
        link = "".join(secrets.choice(char_set) for _ in range(44))

    return HttpResponse(link)


def get_player_links(request, link, year):
    player, season, context = get_admin_info(link, year)
    player_links = (
        PlayerStatus.objects.filter(season=season)
        .values_list("player__username", "player__link")
        .order_by("player__username")
    )

    context["player_links"] = player_links
    return render(request, "player_links.html", context=context)


def update_board_cache(request, link, year):
    get_object_or_404(Player, link=link, is_admin=True)
    season = get_object_or_404(Season, year=year)
    cache_board(season)

    return redirect(reverse("player", args=[link, year]))
