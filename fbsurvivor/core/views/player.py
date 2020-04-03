from django.db.models.functions import Lower
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from fbsurvivor.core.models import Season, Player, PlayerStatus, Pick, Week


def player_redirect(request, link):
    get_object_or_404(Player, link=link)
    current_season = get_object_or_404(Season, is_current=True)
    return redirect(reverse("player_page", args=[link, current_season.year]))


def player_page(request, link, year):
    player = get_object_or_404(Player, link=link)
    season = get_object_or_404(Season, year=year)
    try:
        player_status = PlayerStatus.objects.get(player=player, season=season)
        is_retired = player_status.is_retired
    except PlayerStatus.DoesNotExist:
        player_status = None
        is_retired = False

    can_retire = player_status and (not is_retired) and season.is_current

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

    weeks = Week.objects.for_display(season).values_list("week_num", flat=True)

    board = [
        (ps, list(Pick.objects.for_player_season(ps.player, season)))
        for ps in player_statuses
    ]

    context = {
        "player": player,
        "season": season,
        "player_status": player_status,
        "years": years,
        "can_retire": can_retire,
        "weeks": weeks,
        "board": board,
    }

    return render(request, "player-page.html", context=context)
