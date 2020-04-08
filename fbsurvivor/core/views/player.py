from django.contrib import messages
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from fbsurvivor.core.models import Season, Player, PlayerStatus, Pick, Week


def player_redirect(request, link):
    get_object_or_404(Player, link=link)
    current_season = get_object_or_404(Season, is_current=True)
    return redirect(reverse("player_view", args=[link, current_season.year]))


def player_view(request, link, year):
    player = get_object_or_404(Player, link=link)
    season = get_object_or_404(Season, year=year)

    try:
        ps = PlayerStatus.objects.get(player=player, season=season)
    except PlayerStatus.DoesNotExist:
        if season.is_locked:
            ps = PlayerStatus.objects.filter(player=player).order_by("-season__year")
            latest = ps[0].season.year
            messages.warning(request, f"You did not play in {year}. Here is {latest}")
            return redirect(reverse("player_view", args=[link, latest]))
        else:
            ps = None

    can_retire = ps and (not ps.is_retired) and season.is_current

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
        "player_status": ps,
        "years": years,
        "can_retire": can_retire,
        "weeks": weeks,
        "board": board,
        "player_count": player_statuses.count(),
    }

    return render(request, "player-page.html", context=context)
