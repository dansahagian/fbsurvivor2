from django.contrib import messages
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from fbsurvivor.core.models import Player, Season, PlayerStatus


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


def results():
    return


def remind():
    return
