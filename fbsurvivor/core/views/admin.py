from django.contrib import messages
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from fbsurvivor.core.models import Player, Season, PlayerStatus, Week, Pick
from fbsurvivor.core.tasks import update_player_records


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
    ps = (
        PlayerStatus.objects.filter(season=season)
        .annotate(lower=Lower("player__username"))
        .order_by("-is_paid", "lower")
    )
    context["player_statuses"] = ps
    return render(request, "paid.html", context=context)


def user_paid(request, link, year, user_link):
    player, season, context = get_admin_info(link, year)
    ps = get_object_or_404(PlayerStatus, player__link=user_link, season=season)
    ps.is_paid = True
    ps.save()
    messages.success(request, f"{ps.player.username} marked as paid!")
    return redirect(reverse("paid", args=[link, year]))


def results(request, link, year):
    player, season, context = get_admin_info(link, year)
    current_week = Week.objects.is_current(season)
    teams = (
        Pick.objects.filter(week=current_week, result__isnull=True)
        .values_list("team__team_code", flat=True)
        .distinct()
    )

    context["week"] = current_week
    context["teams"] = teams

    return render(request, "results.html", context=context)


def mark_result(request, link, year, week, team, result):
    player, season, context = get_admin_info(link, year)
    week = get_object_or_404(Week, season=season, week_num=week)
    Pick.objects.filter(week=week, team__team_code=team).update(result=result)

    messages.success(request, f"Picks for week {week} of {team} updated!")
    player_records_updated = update_player_records(year)
    messages.success(request, f"{player_records_updated} player records updated!")
    return redirect(reverse("results", args=[link, year]))


def remind():
    return
